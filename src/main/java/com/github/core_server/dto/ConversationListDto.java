package com.github.core_server.dto;

import java.time.Instant;

public record ConversationListDto(
        String name,
        Instant createdAt
) {
}
