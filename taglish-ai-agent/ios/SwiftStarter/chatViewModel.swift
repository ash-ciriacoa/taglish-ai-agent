import Foundation
import Observation

struct ChatMessage: Identifiable {
    let id = UUID()
    let text: String
    let isUser: Bool
}

@MainActor
@Observable
final class ChatViewModel {
    var messages: [ChatMessage] = []
    var input = ""
    var isSending = false
    var errorText: String?

    private var sessionId: String?
    private let api = APIClient()

    func send() async {
        let text = input.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !text.isEmpty, !isSending else { return }

        input = ""
        errorText = nil
        messages.append(ChatMessage(text: text, isUser: true))
        isSending = true
        defer { isSending = false }

        do {
            let response = try await api.send(message: text, sessionId: sessionId)
            sessionId = response.sessionId
            messages.append(ChatMessage(text: response.reply, isUser: false))
        } catch {
            errorText = "Hindi maabot ang server. Is the API running?"
        }
    }
}
