package com.github.core_server.repository;

import com.github.core_server.entity.MessageEntity;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface MessageRepository extends JpaRepository<MessageEntity, Long> {
    List<MessageEntity> findAllByConversation_ConversationIdOrderByCreatedAtAsc(String conversationId);
}
