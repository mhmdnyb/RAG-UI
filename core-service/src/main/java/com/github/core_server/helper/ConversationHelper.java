package com.github.core_server.helper;

import com.github.core_server.dto.ConversationDeleteDto;
import com.github.core_server.dto.ConversationListDto;
import com.github.core_server.entity.ConversationEntity;
import com.github.core_server.exception.ConversationErrorCode;
import com.github.core_server.exception.ConversationException;
import com.github.core_server.repository.ConversationRepository;
import lombok.AllArgsConstructor;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
@AllArgsConstructor
public class ConversationHelper {

    private final ConversationRepository conversationRepository;

    public void save(ConversationEntity conversation) {
        conversationRepository.save(conversation);
    }

    public void deleteById(Long id) {
        conversationRepository.deleteById(id);
    }

    public ConversationEntity getByConversationId(String conversationId) {
        return conversationRepository.findByConversationId(conversationId)
                .orElseThrow(() -> new ConversationException(ConversationErrorCode.ConversationNotFound));
    }

    public List<ConversationListDto> getUserConversationList(String phoneNumber) {
        return conversationRepository.findConversationListByPhoneNumber(phoneNumber);
    }

    public ConversationDeleteDto getDeleteDto(String conversationId) {
        return conversationRepository.findDeleteConversationByConversationId(conversationId)
                .orElseThrow(() -> new ConversationException(ConversationErrorCode.ConversationNotFound));
    }
}
