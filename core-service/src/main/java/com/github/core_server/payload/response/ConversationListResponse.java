package com.github.core_server.payload.response;

import lombok.Builder;
import lombok.Getter;
import lombok.Setter;

@Getter
@Setter
@Builder
public class ConversationListResponse {
    private String name;
    private String createdAt;
}
