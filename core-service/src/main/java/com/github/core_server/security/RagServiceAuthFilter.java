package com.github.core_server.security;

import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpHeaders;
import org.springframework.stereotype.Component;
import org.springframework.web.filter.OncePerRequestFilter;

import java.io.IOException;

@Component
public class RagServiceAuthFilter extends OncePerRequestFilter {

    @Value("${rag.callback-token}")
    private String expectedToken;

    @Override
    protected void doFilterInternal(
            HttpServletRequest request,
            HttpServletResponse response,
            FilterChain filterChain
    ) throws ServletException, IOException {

        if (!request.getRequestURI()
                .equals("/rag/callback")) {

            filterChain.doFilter(request, response);
            return;
        }

        String authorization =
                request.getHeader(HttpHeaders.AUTHORIZATION);

        String expected =
                "Bearer " + expectedToken;

        if (!expected.equals(authorization)) {
            response.setStatus(
                    HttpServletResponse.SC_UNAUTHORIZED
            );
            return;
        }

        filterChain.doFilter(request, response);
    }
}
