package com.github.core_server.service;


import com.github.core_server.entity.ConversationEntity;
import com.github.core_server.entity.MessageEntity;
import com.github.core_server.entity.UserEntity;
import com.github.core_server.exception.ConversationErrorCode;
import com.github.core_server.exception.ConversationException;
import com.github.core_server.helper.ConversationHelper;
import com.github.core_server.helper.MessageHelper;
import com.github.core_server.helper.UserHelper;
import com.github.core_server.mapper.MessageMapper;
import com.github.core_server.payload.request.SendMessageRequest;
import com.github.core_server.payload.response.MessageResponse;
import lombok.AllArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.security.Principal;
import java.util.List;

@Service
@AllArgsConstructor
public class MessageService {

    private final UserHelper userHelper;
    private final MessageHelper messageHelper;
    private final ConversationHelper conversationHelper;
    private final MessageMapper messageMapper;


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

        messageHelper.save(message);

        return messageMapper.entityToResponse(message);
    }

    public List<MessageResponse> getConversationMessages(String conversationId) {
        return messageHelper.getConversationMessages(conversationId).stream().map(messageMapper::entityToResponse).toList();
    }
}
