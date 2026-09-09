use std::net::SocketAddr;
use std::sync::{Arc, RwLock};
use crate::kv::KvEngine;
use crate::server::http::AppState;

pub struct Server {
    engine: Arc<RwLock<KvEngine>>,
    http_addr: SocketAddr,
    uds_path: Option<String>,
}

impl Server {
    pub fn new(engine: Arc<RwLock<KvEngine>>) -> Self {
        Self {
            engine,
            http_addr: "127.0.0.1:50052".parse().unwrap(),
            uds_path: None,
        }
    }

    pub fn http_addr(mut self, addr: SocketAddr) -> Self {
        self.http_addr = addr;
        self
    }

    pub fn uds_path(mut self, path: impl Into<String>) -> Self {
        self.uds_path = Some(path.into());
        self
    }

    pub async fn serve(self) -> Result<(), Box<dyn std::error::Error>> {
        let state = AppState {
            engine: self.engine.clone(),
        };
        let state_for_uds = state.clone();
        let http_addr = self.http_addr.to_string();
        let uds_path = self.uds_path.clone();

        println!("Starting db6 server");
        println!("HTTP/REST: http://{}", http_addr);

        tokio::spawn(async move {
            if let Err(e) = crate::server::http::start_http(&http_addr, state).await {
                eprintln!("HTTP server error: {}", e);
            }
        });

        if let Some(ref path) = uds_path {
            println!("UDS: {}", path);
            let path_owned = path.clone();
            tokio::spawn(async move {
                if let Err(e) = crate::server::uds::start_uds(&path_owned, state_for_uds).await {
                    eprintln!("UDS server error: {}", e);
                }
            });
        }

        tokio::time::sleep(std::time::Duration::MAX).await;
        Ok(())
    }
}

impl Default for Server {
    fn default() -> Self {
        Self::new(Arc::new(RwLock::new(KvEngine::new("memory").unwrap())))
    }
}

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let server = Server::default()
        .uds_path("/tmp/db6.sock");
    server.serve().await
}