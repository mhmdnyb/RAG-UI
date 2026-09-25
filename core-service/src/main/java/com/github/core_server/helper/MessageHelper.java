package com.github.core_server.helper;

import com.github.core_server.entity.MessageEntity;
import com.github.core_server.repository.MessageRepository;
import lombok.AllArgsConstructor;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
@AllArgsConstructor
public class MessageHelper {

    private final MessageRepository messageRepository;

    public void save(MessageEntity entity) {
        messageRepository.save(entity);
    }

    public List<MessageEntity> getConversationMessages(String conversationId) {
        return messageRepository.findAllByConversation_ConversationIdOrderByCreatedAtAsc(conversationId);
    }
}
