// ========= Contact Form Enhancement =========
document.addEventListener("DOMContentLoaded", () => {
    const contactForm = document.getElementById("contactForm");

    if (contactForm) {
        contactForm.addEventListener("submit", (e) => {
            e.preventDefault();

            const submitBtn = contactForm.querySelector("button");
            submitBtn.disabled = true;
            submitBtn.innerText = "Sending...";

            setTimeout(() => {
                alert("✅ Your message has been sent! We’ll get back to you shortly.");
                contactForm.reset();
                submitBtn.disabled = false;
                submitBtn.innerText = "Submit";
            }, 1500);
        });
    }

    // ========= FAQ Interaction =========
    const faqItems = document.querySelectorAll(".faq-item h3");

    faqItems.forEach((header) => {
        header.addEventListener("click", () => {
            const answer = header.nextElementSibling;
            const isActive = answer.classList.contains("active");

            // Collapse all other answers
            document.querySelectorAll(".faq-item p.active").forEach((p) => {
                p.classList.remove("active");
            });

            // Toggle current one
            if (!isActive) {
                answer.classList.add("active");
                answer.scrollIntoView({ behavior: "smooth", block: "center" });
            }
        });
    });

    // ========= Scroll-To-Top Button (Optional UI) =========
    const scrollBtn = document.createElement("button");
    scrollBtn.innerHTML = "⬆";
    scrollBtn.classList.add("scroll-top-button");
    document.body.appendChild(scrollBtn);

    scrollBtn.addEventListener("click", () => {
        window.scrollTo({ top: 0, behavior: "smooth" });
    });

    window.addEventListener("scroll", () => {
        scrollBtn.style.display = window.scrollY > 300 ? "block" : "none";
    });
});
