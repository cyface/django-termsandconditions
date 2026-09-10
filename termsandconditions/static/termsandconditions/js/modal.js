/* Wires up the dismiss button on the "terms have changed" modal.
   The modal is rendered visible, so it still shows without JavaScript. */
(function () {
    "use strict";

    function dismiss() {
        var modals = document.getElementsByClassName("termsandconditions-modal");
        for (var i = 0; i < modals.length; i++) {
            modals[i].hidden = true;
        }
    }

    function init() {
        document.querySelectorAll("[data-toc-dismiss]").forEach(function (button) {
            button.addEventListener("click", dismiss);
        });
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", init);
    } else {
        init();
    }
})();
