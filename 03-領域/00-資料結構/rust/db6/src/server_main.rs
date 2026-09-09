use db6::server::Server;

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let server = Server::default()
        .uds_path("/tmp/db6.sock");
    server.serve().await
}