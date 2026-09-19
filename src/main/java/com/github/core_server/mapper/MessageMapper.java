package com.github.core_server.mapper;

import com.github.core_server.entity.ConversationEntity;
import com.github.core_server.entity.MessageEntity;
import com.github.core_server.payload.request.SendMessageRequest;
import com.github.core_server.payload.response.MessageResponse;
import org.springframework.stereotype.Component;

@Component
public class MessageMapper {

    public MessageEntity toEntity(SendMessageRequest request, ConversationEntity conversation) {
        return MessageEntity.builder()
                .content(request.getContent())
                .conversation(conversation)
                .build();
    }

    public MessageResponse entityToResponse(MessageEntity entity) {
        return MessageResponse.builder()
                .messageId(entity.getMessageId())
                .content(entity.getContent())
                .sendTime(entity.getCreatedAt().toString().substring(0, 10))
                .conversationId(entity.getConversation().getConversationId())
                .build();
    }
}
