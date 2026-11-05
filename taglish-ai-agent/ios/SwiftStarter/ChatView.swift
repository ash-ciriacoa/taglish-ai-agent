import SwiftUI

struct ChatView: View {
    @State private var model = ChatViewModel()

    var body: some View {
        VStack(spacing: 0) {
            ScrollViewReader { proxy in
                ScrollView {
                    LazyVStack(spacing: 8) {
                        ForEach(model.messages) { message in
                            bubble(message).id(message.id)
                        }
                    }
                    .padding()
                }
                .onChange(of: model.messages.count) {
                    if let last = model.messages.last {
                        withAnimation { proxy.scrollTo(last.id, anchor: .bottom) }
                    }
                }
            }

            if let error = model.errorText {
                Text(error).font(.footnote).foregroundStyle(.red).padding(.horizontal)
            }

            HStack {
                TextField("Message / Mensahe", text: $model.input)
                    .textFieldStyle(.roundedBorder)
                    .onSubmit { Task { await model.send() } }
                Button("Send") { Task { await model.send() } }
                    .disabled(model.isSending)
            }
            .padding()
        }
    }

    private func bubble(_ message: ChatMessage) -> some View {
        HStack {
            if message.isUser { Spacer(minLength: 40) }
            Text(message.text)
                .padding(10)
                .background(message.isUser ? Color.accentColor : Color(.secondarySystemBackground))
                .foregroundStyle(message.isUser ? Color.white : Color.primary)
                .clipShape(RoundedRectangle(cornerRadius: 14))
            if !message.isUser { Spacer(minLength: 40) }
        }
    }
}

#Preview { ChatView() }
