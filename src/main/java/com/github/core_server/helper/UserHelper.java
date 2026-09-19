package com.github.core_server.helper;

import com.github.core_server.entity.UserEntity;
import com.github.core_server.exception.UserErrorCode;
import com.github.core_server.exception.UserException;
import com.github.core_server.repository.UserRepository;
import com.github.core_server.security.CustomUserDetails;
import lombok.AllArgsConstructor;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.stereotype.Service;

@Service
@AllArgsConstructor
public class UserHelper {

    private final UserRepository userRepository;

    public UserEntity getCurrentUser() {
        Authentication authentication = SecurityContextHolder.getContext().getAuthentication();

        CustomUserDetails userDetails = (CustomUserDetails) authentication.getPrincipal();

        Long userId = userDetails.getUser().getId();

        return userRepository.findById(userId)
                .orElseThrow(() -> new UserException(UserErrorCode.UserNotFound));
    }

    public UserEntity findUserByPhoneNumber(String phoneNumber) {
        return userRepository.findByPhoneNumber(phoneNumber)
                .orElseThrow(() -> new UserException(UserErrorCode.UserNotFound));
    }

    public void save(UserEntity user) {
        userRepository.save(user);
    }

    public boolean existsByPhoneNumber(String phoneNumber) {
        return userRepository.existsByPhoneNumber(phoneNumber);
    }
}
