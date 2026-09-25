package com.github.core_server.controller;

import com.github.core_server.payload.response.ApiResponse;
import com.github.core_server.payload.response.ConversationListResponse;
import com.github.core_server.payload.response.ConversationResponse;
import com.github.core_server.service.ConversationService;
import lombok.AllArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/chat-list")
@AllArgsConstructor
public class ChatListController {

    private final ConversationService conversationService;

    @GetMapping
    public ApiResponse<List<ConversationListResponse>> getUserChats() {
        return conversationService.getUserConversations();
    }

    @PostMapping
    public ApiResponse<ConversationResponse> createConversation() {
        return conversationService.createConversation();
    }

    @DeleteMapping("/{chatId}")
    public ApiResponse<Void> deleteConversation(@PathVariable String chatId) {
        return conversationService.deleteConversation(chatId);
    }
}
