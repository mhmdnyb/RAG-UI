package com.github.core_server.service;

import com.github.core_server.dto.ConversationDeleteDto;
import com.github.core_server.entity.ConversationEntity;
import com.github.core_server.entity.UserEntity;
import com.github.core_server.exception.ConversationErrorCode;
import com.github.core_server.exception.ConversationException;
import com.github.core_server.helper.ConversationHelper;
import com.github.core_server.helper.MessageHelper;
import com.github.core_server.helper.UserHelper;
import com.github.core_server.mapper.ConversationMapper;
import com.github.core_server.payload.response.ApiResponse;
import com.github.core_server.payload.response.ConversationListResponse;
import com.github.core_server.payload.response.ConversationResponse;
import lombok.AllArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.Objects;

@Service
@AllArgsConstructor
public class ConversationService {

    private final ConversationHelper conversationHelper;
    private final ConversationMapper conversationMapper;
    private final UserHelper userHelper;
    private final MessageHelper messageHelper;

    public ApiResponse<ConversationResponse> createConversation(){

        UserEntity currentUser = userHelper.getCurrentUser();

        ConversationEntity conversation = new ConversationEntity(currentUser);

        conversationHelper.save(conversation);

        return ApiResponse.<ConversationResponse>builder()
                .status("OK")
                .data(conversationMapper.entityToResponse(conversation))
                .build();
    }

    public ApiResponse<List<ConversationListResponse>> getUserConversations() {

        UserEntity currentUser = userHelper.getCurrentUser();

        List<ConversationListResponse> conversations =
                conversationHelper.getUserConversationList(currentUser.getPhoneNumber())
                        .stream()
                        .map(conversationMapper::listDtoToResponse)
                        .toList();

        return ApiResponse.<List<ConversationListResponse>>builder()
                .status("OK")
                .data(conversations)
                .build();

    }

    @Transactional
    public ApiResponse<Void> deleteConversation(String conversationId) {

        UserEntity currentUser = userHelper.getCurrentUser();

        ConversationDeleteDto dto = conversationHelper.getDeleteDto(conversationId);

        if (Objects.equals(dto.userId(), currentUser.getId())) {
            messageHelper.deleteByConversationId(dto.ConversationId());
            conversationHelper.deleteById(dto.ConversationId());

            return ApiResponse.<Void>builder()
                    .status("OK")
                    .build();
        } else {
            throw new ConversationException(ConversationErrorCode.ConversationNotOwned);
        }
    }

}
