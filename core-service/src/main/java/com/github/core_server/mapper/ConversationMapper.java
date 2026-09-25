package com.github.core_server.mapper;

import com.github.core_server.dto.ConversationListDto;
import com.github.core_server.entity.ConversationEntity;
import com.github.core_server.payload.response.ConversationListResponse;
import com.github.core_server.payload.response.ConversationResponse;
import org.springframework.stereotype.Component;

@Component
public class ConversationMapper {

    public ConversationResponse entityToResponse(ConversationEntity entity) {
        return ConversationResponse.builder()
                .conversationId(entity.getConversationId())
                .createdAt(entity.getCreatedAt().toString().substring(0, 10))
                .name(entity.getName())
                .build();
    }

    public ConversationListResponse listDtoToResponse(ConversationListDto dto) {
        return ConversationListResponse.builder()
                .name(dto.name())
                .createdAt(dto.createdAt().toString().substring(0, 10))
                .build();
    }

}
