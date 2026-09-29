package com.github.core_server.service;


import com.github.core_server.config.RagClient;
import com.github.core_server.entity.ConversationEntity;
import com.github.core_server.entity.MessageEntity;
import com.github.core_server.entity.UserEntity;
import com.github.core_server.enums.MessageStatus;
import com.github.core_server.exception.ConversationErrorCode;
import com.github.core_server.exception.ConversationException;
import com.github.core_server.helper.ConversationHelper;
import com.github.core_server.helper.MessageHelper;
import com.github.core_server.helper.UserHelper;
import com.github.core_server.mapper.MessageMapper;
import com.github.core_server.payload.request.RagCallBackRequest;
import com.github.core_server.payload.request.RagQueryRequest;
import com.github.core_server.payload.request.SendMessageRequest;
import com.github.core_server.payload.response.MessageResponse;
import com.github.core_server.payload.response.RagCallBackResponse;
import com.github.core_server.payload.response.RagQueryResponse;
import lombok.AllArgsConstructor;
import org.springframework.messaging.simp.SimpMessagingTemplate;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import tools.jackson.databind.ObjectMapper;

import java.security.Principal;
import java.util.List;

@Service
@AllArgsConstructor
public class MessageService {

    private final RagClient ragClient;
    private final UserHelper userHelper;
    private final MessageHelper messageHelper;
    private final ConversationHelper conversationHelper;
    private final MessageMapper messageMapper;
    private final ObjectMapper objectMapper;
    private final SimpMessagingTemplate messagingTemplate;


    @Transactional
    public MessageResponse sendMessage(
            SendMessageRequest request,
            Principal principal
    ) {

        UserEntity currentUser = userHelper.findUserByPhoneNumber(principal.getName());

        ConversationEntity conversation =
                conversationHelper.getByConversationId(
                        request.getConversationId()
                );

        if (!conversation.getUser().getId().equals(currentUser.getId())) {
            throw new ConversationException(ConversationErrorCode.ConversationNotOwned);
        }

        MessageEntity message = messageMapper.toEntity(request, conversation);
        message.setStatus(MessageStatus.PROCESSING);

        messageHelper.save(message);

        try {
            RagQueryResponse response = sendRagQuery(message);

            if (!response.getStatus().equals("OK")) {
                message.setStatus(MessageStatus.FAILED);
                messageHelper.save(message);
            }
        } catch (Exception e) {
            message.setStatus(MessageStatus.FAILED);
            messageHelper.save(message);
        }

        return messageMapper.entityToResponse(message);
    }

    public void botSendMessage(MessageEntity message, String conversationId) {

        messageHelper.save(message);

        MessageResponse response = messageMapper.entityToResponse(message);

        messagingTemplate.convertAndSend(
                "/topic/chat/" + conversationId,
                response
        );

    }

    public List<MessageResponse> getConversationMessages(String conversationId) {
        return messageHelper.getConversationMessages(conversationId).stream().map(messageMapper::entityToResponse).toList();
    }

    public RagQueryResponse sendRagQuery(MessageEntity message) {

        RagQueryRequest request = messageMapper.entityToQuery(message);

         return ragClient.sendQuestion(request);
    }

    public RagCallBackResponse getRagResponse(RagCallBackRequest request) {

        ConversationEntity conversation =
                conversationHelper.getByConversationId(
                        request.getConversationId()
                );

        String sources = objectMapper.writeValueAsString(request.getSources());

        MessageEntity message = messageMapper.CallBackToEntity(request, conversation, sources);

        botSendMessage(message, request.getConversationId());

        return RagCallBackResponse.builder()
                .status("received")
                .build();

    }
}
