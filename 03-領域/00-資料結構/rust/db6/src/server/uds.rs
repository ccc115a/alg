use std::path::Path;
use tokio::net::{UnixSocket, UnixStream};
use tokio::io::{AsyncReadExt, AsyncWriteExt};
use crate::server::http::AppState;
use crate::server::websocket::{WsRequest, WsResponse};

pub async fn start_uds(path: &str, state: AppState) -> Result<(), Box<dyn std::error::Error + Send + Sync>> {
    let socket = UnixSocket::new_stream()?;
    socket.bind(path)?;
    let listener = socket.listen(1024)?;

    println!("UDS server listening on {}", path);

    loop {
        match listener.accept().await {
            Ok((stream, _)) => {
                let state = state.clone();
                tokio::spawn(async move {
                    if let Err(e) = handle_connection(stream, state).await {
                        eprintln!("UDS connection error: {}", e);
                    }
                });
            }
            Err(e) => {
                eprintln!("UDS accept error: {}", e);
            }
        }
    }
}

async fn handle_connection(mut stream: UnixStream, state: AppState) -> Result<(), Box<dyn std::error::Error + Send + Sync>> {
    let mut buf = vec![0u8; 4096];
    let mut cursor = 0;

    loop {
        let n = stream.read(&mut buf[cursor..]).await?;
        if n == 0 {
            break;
        }
        cursor += n;

        while let Some(pos) = buf[..cursor].iter().position(|&b| b == b'\n') {
            let line = String::from_utf8_lossy(&buf[..pos]).to_string();
            cursor -= pos + 1;
            buf.copy_within(pos + 1.., 0);

            let request: WsRequest = match serde_json::from_str(&line) {
                Ok(req) => req,
                Err(e) => {
                    let resp = WsResponse {
                        id: None,
                        result: None,
                        error: Some(format!("Invalid JSON: {}", e)),
                    };
                    if let Err(_) = write_response(&mut stream, resp).await {
                        return Ok(());
                    }
                    continue;
                }
            };

            let resp = crate::server::websocket::handle_request(request, &state).await;
            if let Err(e) = write_response(&mut stream, resp).await {
                return Ok(());
            }
        }
    }

    Ok(())
}

async fn write_response(stream: &mut UnixStream, resp: WsResponse) -> Result<(), Box<dyn std::error::Error + Send + Sync>> {
    let json = serde_json::to_string(&resp)?;
    stream.write_all(json.as_bytes()).await?;
    stream.write_all(b"\n").await?;
    Ok(())
}