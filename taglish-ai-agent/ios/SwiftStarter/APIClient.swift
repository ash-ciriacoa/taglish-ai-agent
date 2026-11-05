import Foundation

struct ChatRequest: Encodable {
    let message: String
    let sessionId: String?

    enum CodingKeys: String, CodingKey {
        case message
        case sessionId = "session_id"
    }
}

struct ChatResponse: Decodable {
    let sessionId: String
    let reply: String
    let stoppedReason: String

    enum CodingKeys: String, CodingKey {
        case sessionId = "session_id"
        case reply
        case stoppedReason = "stopped_reason"
    }
}

struct APIClient {
    // Simulator can use localhost. On a physical iPhone, use your Mac's LAN IP.
    var baseURL = URL(string: "http://localhost:8000")!

    func send(message: String, sessionId: String?) async throws -> ChatResponse
    {
        var request = URLRequest(url: baseURL.appendingPathComponent("chat"))
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.httpBody = try JSONEncoder().encode(ChatRequest(message: message, sessionId: sessionId))

        let (data, response) = try await URLSession.shared.data(for: request)
        guard let http = response as? HTTPURLResponse, (200..<300).contains(http.statusCode) else {
            throw URLError(.badServerResponse)
        }
        return try JSONDecoder().decode(ChatResponse.self, from: data)
    }
}

