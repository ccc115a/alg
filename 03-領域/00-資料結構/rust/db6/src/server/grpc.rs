// gRPC transport - to be implemented
// Requires manual service implementation due to tonic-build 0.14 changes

pub async fn start_grpc(_addr: &str) -> Result<(), Box<dyn std::error::Error>> {
    println!("gRPC transport not yet implemented");
    Ok(())
}