use axum::{
    extract::{
        State,
        WebSocketUpgrade,
        ws::{Message, WebSocket},
    },
    response::IntoResponse,
};
use futures_util::{StreamExt, SinkExt};
use serde::{Deserialize, Serialize};
use crate::kv::KvEngine;
use crate::{KvApi, StorageEngine, FtsIndex, Msgq, SqlExecutor};
use crate::server::http::AppState;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct WsRequest {
    pub method: String,
    pub id: Option<u64>,
    pub params: serde_json::Value,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct WsResponse {
    pub id: Option<u64>,
    pub result: Option<serde_json::Value>,
    pub error: Option<String>,
}

pub async fn ws_handler(ws: WebSocketUpgrade, State(state): State<AppState>) -> impl IntoResponse {
    ws.on_upgrade(|socket| handle_socket(socket, state))
}

async fn handle_socket(mut socket: WebSocket, state: AppState) {
    while let Some(msg) = socket.recv().await {
        if let Ok(msg) = msg {
            if let Message::Text(text) = msg {
                if let Ok(req) = serde_json::from_str::<WsRequest>(&text) {
                    let resp = handle_request(req, &state).await;
                    if let Ok(resp_json) = serde_json::to_string(&resp) {
                        if socket.send(Message::Text(resp_json.into())).await.is_err() {
                            break;
                        }
                    }
                }
            }
        } else {
            break;
        }
    }
}

pub async fn handle_request(req: WsRequest, state: &AppState) -> WsResponse {
    match req.method.as_str() {
        "health" => WsResponse { id: req.id, result: Some("OK".into()), error: None },

        "kv_put" => {
            let table_id = req.params.get("table_id").and_then(|v| v.as_i64()).unwrap_or(1) as u32;
            let key = req.params.get("key").and_then(|v| v.as_str()).unwrap_or("");
            let value = req.params.get("value").and_then(|v| v.as_str()).unwrap_or("");

            let mut engine = state.engine.write().unwrap();
            match KvApi::put(&mut *engine, table_id, key.as_bytes(), value.as_bytes()) {
                Ok(_) => WsResponse { id: req.id, result: Some(serde_json::json!({"status": "ok"})), error: None },
                Err(e) => WsResponse { id: req.id, result: None, error: Some(e.to_string()) },
            }
        }

        "kv_get" => {
            let table_id = req.params.get("table_id").and_then(|v| v.as_i64()).unwrap_or(1) as u32;
            let key = req.params.get("key").and_then(|v| v.as_str()).unwrap_or("");

            let mut engine = state.engine.write().unwrap();
            match KvApi::get(&mut *engine, table_id, key.as_bytes()) {
                Ok(value) => WsResponse {
                    id: req.id,
                    result: Some(serde_json::json!({
                        "found": value.is_some(),
                        "value": value.map(|v| String::from_utf8_lossy(&v).to_string())
                    })),
                    error: None,
                },
                Err(e) => WsResponse { id: req.id, result: None, error: Some(e.to_string()) },
            }
        }

        "kv_delete" => {
            let table_id = req.params.get("table_id").and_then(|v| v.as_i64()).unwrap_or(1) as u32;
            let key = req.params.get("key").and_then(|v| v.as_str()).unwrap_or("");

            let mut engine = state.engine.write().unwrap();
            match KvApi::delete(&mut *engine, table_id, key.as_bytes()) {
                Ok(_) => WsResponse { id: req.id, result: Some(serde_json::json!({"status": "ok"})), error: None },
                Err(e) => WsResponse { id: req.id, result: None, error: Some(e.to_string()) },
            }
        }

        "kv_scan" => {
            let table_id = req.params.get("table_id").and_then(|v| v.as_i64()).unwrap_or(1) as u32;
            let start = req.params.get("start").and_then(|v| v.as_str()).unwrap_or("");
            let end = req.params.get("end").and_then(|v| v.as_str()).unwrap_or("");

            let mut engine = state.engine.write().unwrap();
            match KvApi::scan(&mut *engine, table_id, start.as_bytes(), end.as_bytes()) {
                Ok(pairs) => {
                    let result: Vec<_> = pairs.into_iter().map(|(k, v)| {
                        serde_json::json!({
                            "key": String::from_utf8_lossy(&k),
                            "value": String::from_utf8_lossy(&v)
                        })
                    }).collect();
                    WsResponse { id: req.id, result: Some(serde_json::json!({"pairs": result})), error: None }
                }
                Err(e) => WsResponse { id: req.id, result: None, error: Some(e.to_string()) },
            }
        }

        "kv_batch_put" => {
            let table_id = req.params.get("table_id").and_then(|v| v.as_i64()).unwrap_or(1) as u32;
            let pairs: Vec<_> = req.params.get("pairs")
                .and_then(|v| v.as_array())
                .map(|arr| {
                    arr.iter().filter_map(|p| {
                        Some((
                            p.get("key")?.as_str()?.as_bytes().to_vec(),
                            p.get("value")?.as_str()?.as_bytes().to_vec(),
                        ))
                    }).collect::<Vec<_>>()
                })
                .unwrap_or_default();

            let mut engine = state.engine.write().unwrap();
            match KvApi::batch_put(&mut *engine, table_id, pairs) {
                Ok(_) => WsResponse { id: req.id, result: Some(serde_json::json!({"status": "ok"})), error: None },
                Err(e) => WsResponse { id: req.id, result: None, error: Some(e.to_string()) },
            }
        }

        "kv_range_delete" => {
            let table_id = req.params.get("table_id").and_then(|v| v.as_i64()).unwrap_or(1) as u32;
            let start = req.params.get("start").and_then(|v| v.as_str()).unwrap_or("");
            let end = req.params.get("end").and_then(|v| v.as_str()).unwrap_or("");

            let mut engine = state.engine.write().unwrap();
            match KvApi::range_delete(&mut *engine, table_id, start.as_bytes(), end.as_bytes()) {
                Ok(_) => WsResponse { id: req.id, result: Some(serde_json::json!({"status": "ok"})), error: None },
                Err(e) => WsResponse { id: req.id, result: None, error: Some(e.to_string()) },
            }
        }

        "kv_stats" => {
            let engine = state.engine.read().unwrap();
            let s = StorageEngine::stats(&*engine);
            WsResponse {
                id: req.id,
                result: Some(serde_json::json!({
                    "key_count": s.key_count,
                    "size_bytes": s.size_bytes,
                    "engine": s.engine
                })),
                error: None,
            }
        }

        "sql_execute" => {
            let sql = req.params.get("sql").and_then(|v| v.as_str()).unwrap_or("");
            let mut exec = SqlExecutor::new(crate::engine::HashMemoryEngine::new());

            match exec.execute(sql) {
                Ok(result) => WsResponse {
                    id: req.id,
                    result: Some(serde_json::json!({
                        "columns": result.columns,
                        "rows": result.rows,
                        "affected": result.affected
                    })),
                    error: None,
                },
                Err(e) => WsResponse { id: req.id, result: None, error: Some(e.to_string()) },
            }
        }

        "fts_insert" => {
            let doc_id = req.params.get("doc_id").and_then(|v| v.as_i64()).unwrap_or(0) as u64;
            let text = req.params.get("text").and_then(|v| v.as_str()).unwrap_or("");

            let mut engine = state.engine.write().unwrap();
            let mut fts = FtsIndex::new(&mut *engine);
            match fts.insert(doc_id, text) {
                Ok(_) => WsResponse { id: req.id, result: Some(serde_json::json!({"status": "ok"})), error: None },
                Err(e) => WsResponse { id: req.id, result: None, error: Some(e.to_string()) },
            }
        }

        "fts_search" => {
            let query = req.params.get("query").and_then(|v| v.as_str()).unwrap_or("");

            let mut engine = state.engine.write().unwrap();
            let fts = FtsIndex::new(&mut *engine);
            match fts.search(query) {
                Ok(doc_ids) => WsResponse {
                    id: req.id,
                    result: Some(serde_json::json!({"doc_ids": doc_ids})),
                    error: None,
                },
                Err(e) => WsResponse { id: req.id, result: None, error: Some(e.to_string()) },
            }
        }

        "fts_search_bm25" => {
            let query = req.params.get("query").and_then(|v| v.as_str()).unwrap_or("");

            let mut engine = state.engine.write().unwrap();
            let fts = FtsIndex::new(&mut *engine);
            match fts.search_bm25(query) {
                Ok(results) => {
                    let formatted: Vec<_> = results.into_iter().map(|(doc_id, score)| {
                        serde_json::json!({"doc_id": doc_id, "score": score})
                    }).collect();
                    WsResponse { id: req.id, result: Some(serde_json::json!({"results": formatted})), error: None }
                }
                Err(e) => WsResponse { id: req.id, result: None, error: Some(e.to_string()) },
            }
        }

        "queue_create" => {
            let name = req.params.get("name").and_then(|v| v.as_str()).unwrap_or("");
            let msgq = Msgq::new("memory").expect("msgq create failed");
            let _queue = msgq.queue(name);
            WsResponse { id: req.id, result: Some(serde_json::json!({"status": "ok"})), error: None }
        }

        "queue_enqueue" => {
            let name = req.params.get("name").and_then(|v| v.as_str()).unwrap_or("");
            let payload = req.params.get("payload").and_then(|v| v.as_str()).unwrap_or("");
            let timeout = req.params.get("timeout").and_then(|v| v.as_i64()).unwrap_or(30) as u64;

            let msgq = Msgq::new("memory").expect("msgq create failed");
            let mut queue = msgq.queue(name);
            match queue.enqueue(payload.as_bytes().to_vec(), timeout) {
                Ok(msg_id) => WsResponse { id: req.id, result: Some(serde_json::json!({"msg_id": msg_id})), error: None },
                Err(e) => WsResponse { id: req.id, result: None, error: Some(e.to_string()) },
            }
        }

        "queue_dequeue" => {
            let name = req.params.get("name").and_then(|v| v.as_str()).unwrap_or("");
            let wait_timeout = req.params.get("wait_timeout").and_then(|v| v.as_i64()).unwrap_or(0) as u64;

            let msgq = Msgq::new("memory").expect("msgq create failed");
            let mut queue = msgq.queue(name);
            match queue.dequeue(wait_timeout) {
                Ok(Some(msg)) => WsResponse {
                    id: req.id,
                    result: Some(serde_json::json!({
                        "msg_id": msg.id,
                        "payload": String::from_utf8_lossy(&msg.payload),
                        "delivery_count": msg.delivery_count
                    })),
                    error: None,
                },
                Ok(None) => WsResponse { id: req.id, result: Some(serde_json::json!({"msg_id": null, "payload": null, "delivery_count": 0})), error: None },
                Err(e) => WsResponse { id: req.id, result: None, error: Some(e.to_string()) },
            }
        }

        "queue_ack" => {
            let name = req.params.get("name").and_then(|v| v.as_str()).unwrap_or("");
            let msg_id = req.params.get("msg_id").and_then(|v| v.as_str()).unwrap_or("");

            let msgq = Msgq::new("memory").expect("msgq create failed");
            let mut queue = msgq.queue(name);
            match queue.ack(&msg_id) {
                Ok(_) => WsResponse { id: req.id, result: Some(serde_json::json!({"status": "ok"})), error: None },
                Err(e) => WsResponse { id: req.id, result: None, error: Some(e.to_string()) },
            }
        }

        "queue_stats" => {
            let name = req.params.get("name").and_then(|v| v.as_str()).unwrap_or("");

            let msgq = Msgq::new("memory").expect("msgq create failed");
            match msgq.stats(name) {
                Ok(stats) => WsResponse {
                    id: req.id,
                    result: Some(serde_json::json!({
                        "name": stats.name,
                        "length": stats.length,
                        "total_enqueued": stats.total_enqueued,
                        "completed": stats.completed,
                        "nacked": stats.nacked
                    })),
                    error: None,
                },
                Err(e) => WsResponse { id: req.id, result: None, error: Some(e.to_string()) },
            }
        }

        "queue_list" => {
            let msgq = Msgq::new("memory").expect("msgq create failed");
            match msgq.list_queues() {
                Ok(queues) => WsResponse { id: req.id, result: Some(serde_json::json!({"queues": queues})), error: None },
                Err(e) => WsResponse { id: req.id, result: None, error: Some(e.to_string()) },
            }
        }

        "pubsub_publish" => {
            let channel = req.params.get("channel").and_then(|v| v.as_str()).unwrap_or("");
            let payload = req.params.get("payload").and_then(|v| v.as_str()).unwrap_or("");

            let msgq = Msgq::new("memory").expect("msgq create failed");
            let mut pubsub = msgq.pubsub();
            match pubsub.publish(channel, payload.as_bytes().to_vec()) {
                Ok(msg_id) => WsResponse { id: req.id, result: Some(serde_json::json!({"msg_id": msg_id})), error: None },
                Err(e) => WsResponse { id: req.id, result: None, error: Some(e.to_string()) },
            }
        }

        _ => WsResponse {
            id: req.id,
            result: None,
            error: Some(format!("Unknown method: {}", req.method)),
        },
    }
}

pub fn create_ws_router(state: AppState) -> axum::Router {
    use axum::routing::get;

    axum::Router::new()
        .route("/ws", get(ws_handler))
        .with_state(state)
}