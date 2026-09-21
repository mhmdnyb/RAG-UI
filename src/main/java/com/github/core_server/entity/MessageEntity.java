package com.github.core_server.entity;


import com.aventrix.jnanoid.jnanoid.NanoIdUtils;
import com.github.core_server.dto.RagSourceDto;
import com.github.core_server.enums.MessageStatus;
import jakarta.persistence.*;
import lombok.*;

import java.time.Instant;
import java.util.List;

@Entity
@Table(name = "message")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class MessageEntity {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false, updatable = false,
            unique = true, length = 21)
    private String messageId;

    @ManyToOne
    @JoinColumn(name = "conversation_id")
    private ConversationEntity conversation;

    @Column(nullable = false, columnDefinition = "TEXT")
    private String content;

    @Column(nullable = false, updatable = false)
    private Instant createdAt;

    @Enumerated(EnumType.STRING)
    @Builder.Default
    private MessageStatus status = MessageStatus.NONE;

    private boolean botMessage = false;

    @Column(columnDefinition = "TEXT")
    private String sources = null;

    @PrePersist
    public void onCreate(){
        Instant now = Instant.now();
        createdAt = now;
        messageId = NanoIdUtils.randomNanoId();
    }
}