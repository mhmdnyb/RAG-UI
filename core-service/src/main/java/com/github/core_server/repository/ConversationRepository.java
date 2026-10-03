package com.github.core_server.repository;

import com.github.core_server.dto.ConversationDeleteDto;
import com.github.core_server.dto.ConversationListDto;
import com.github.core_server.entity.ConversationEntity;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface ConversationRepository extends JpaRepository<ConversationEntity, Long> {
    @Query("""
    SELECT new com.github.core_server.dto.ConversationListDto(
        c.conversationId,
        c.name,
        c.createdAt
    )
    FROM ConversationEntity c
    WHERE c.user.phoneNumber = :phoneNumber
    ORDER BY  c.createdAt DESC 
""")
    List<ConversationListDto> findConversationListByPhoneNumber(
            @Param("phoneNumber") String phoneNumber
    );

    @Query("""
    SELECT new com.github.core_server.dto.ConversationDeleteDto(
        c.id,
        c.user.id
    )
    FROM ConversationEntity c
    WHERE c.conversationId = :conversationId
""")
    Optional<ConversationDeleteDto> findDeleteConversationByConversationId(
            @Param("conversationId") String conversationId
    );

    Optional<ConversationEntity> findByConversationId(String conversationId);
}
