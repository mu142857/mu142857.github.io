/**
 * Typewriter effect for sidebar bio text
 * Reveals text character by character
 */
(function () {
    'use strict';

    const TYPING_SPEED = 15; // milliseconds per character (faster)

    function typeWriter(element, html, index, callback) {
        if (index < html.length) {
            // Handle HTML tags - add them instantly
            if (html[index] === '<') {
                let tagEnd = html.indexOf('>', index);
                if (tagEnd !== -1) {
                    element.innerHTML = html.substring(0, tagEnd + 1);
                    setTimeout(() => typeWriter(element, html, tagEnd + 1, callback), 0);
                    return;
                }
            }

            element.innerHTML = html.substring(0, index + 1);
            setTimeout(() => typeWriter(element, html, index + 1, callback), TYPING_SPEED);
        } else if (callback) {
            callback();
        }
    }

    function initTypewriter() {
        // For pages with p tag in header (projects, games, contact), apply to p
        const headerP = document.querySelector('#header .inner p');
        if (headerP) {
            const originalHTML = headerP.innerHTML;
            headerP.innerHTML = '';
            headerP.style.visibility = 'visible';
            
            setTimeout(() => {
                typeWriter(headerP, originalHTML, 0);
            }, 300);
            return;
        }

        // For homepage, apply to .typewriter-text span
        const typewriterSpan = document.querySelector('.typewriter-text');
        if (typewriterSpan) {
            const originalHTML = typewriterSpan.innerHTML;
            typewriterSpan.innerHTML = '';
            typewriterSpan.style.visibility = 'visible';
            
            setTimeout(() => {
                typeWriter(typewriterSpan, originalHTML, 0);
            }, 300);
        }
    }

    // Run when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initTypewriter);
    } else {
        initTypewriter();
    }
})();
