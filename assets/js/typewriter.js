/**
 * Typewriter effect for sidebar bio text
 * Reveals text character by character
 */
(function () {
    'use strict';

    const TYPING_SPEED = 35; // milliseconds per character

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
        const headerInner = document.querySelector('#header .inner h1');
        if (!headerInner) return;

        const originalHTML = headerInner.innerHTML;
        headerInner.innerHTML = '';
        headerInner.style.visibility = 'visible';

        // Small delay before starting
        setTimeout(() => {
            typeWriter(headerInner, originalHTML, 0);
        }, 300);
    }

    // Run when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initTypewriter);
    } else {
        initTypewriter();
    }
})();
