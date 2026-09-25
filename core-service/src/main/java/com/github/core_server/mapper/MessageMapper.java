package com.github.core_server.mapper;

import com.github.core_server.entity.ConversationEntity;
import com.github.core_server.entity.MessageEntity;
import com.github.core_server.enums.MessageStatus;
import com.github.core_server.payload.request.RagCallBackRequest;
import com.github.core_server.payload.request.RagQueryRequest;
import com.github.core_server.payload.request.SendMessageRequest;
import com.github.core_server.payload.response.MessageResponse;
import org.springframework.stereotype.Component;

@Component
public class MessageMapper {

    public MessageEntity toEntity(SendMessageRequest request, ConversationEntity conversation) {
        return MessageEntity.builder()
                .content(request.getContent())
                .conversation(conversation)
                .botMessage(false)
                .status(MessageStatus.NONE)
                .build();
    }

    public MessageResponse entityToResponse(MessageEntity entity) {
        return MessageResponse.builder()
                .messageId(entity.getMessageId())
                .content(entity.getContent())
                .sendTime(entity.getCreatedAt().toString().substring(0, 10))
                .conversationId(entity.getConversation().getConversationId())
                .botMessage(entity.isBotMessage())
                .sources(entity.getSources())
                .status(entity.getStatus().toString())
                .build();
    }

    public RagQueryRequest entityToQuery(MessageEntity entity) {
        return RagQueryRequest.builder()
                .conversationId(entity.getConversation().getConversationId())
                .question(entity.getContent())
                .build();
    }

    public MessageEntity CallBackToEntity(RagCallBackRequest request, ConversationEntity conversation, String sources) {
        return MessageEntity.builder()
                .botMessage(true)
                .conversation(conversation)
                .content(request.getAnswer())
                .sources(sources)
                .status(MessageStatus.NONE)
                .build();
    }
}
