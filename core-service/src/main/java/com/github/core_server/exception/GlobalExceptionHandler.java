package com.github.core_server.exception;

import com.github.core_server.payload.response.ApiResponse;
import com.github.core_server.payload.response.ErrorResponse;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;

@RestControllerAdvice
public class GlobalExceptionHandler {

    @ExceptionHandler(UserException.class)
    public ApiResponse<ErrorResponse> handleUserException(UserException exception) {
        return ApiResponse.<ErrorResponse>builder()
                .status("error")
                .data(
                        ErrorResponse.builder()
                        .message(exception.getMessage())
                        .code(exception.getCode())
                        .build()
                )
                .build();
    }

    @ExceptionHandler(ConversationException.class)
    public ApiResponse<ErrorResponse> handleConversationException(ConversationException exception) {
        return ApiResponse.<ErrorResponse>builder()
                .status("error")
                .data(
                        ErrorResponse.builder()
                        .message(exception.getMessage())
                        .code(exception.getCode())
                        .build()
                )
                .build();
    }
}