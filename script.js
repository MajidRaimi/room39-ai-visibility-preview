/* Room 39 — one-page offer site behavior
   - scroll-reveal via IntersectionObserver (transform/opacity only)
   - plan buttons preselect the form's "interest" field and scroll to it
   - lead form validation + submission with a graceful preview fallback

   PRODUCTION NOTE: set LEAD_ENDPOINT to your form/CRM URL. When it is empty,
   the page runs in preview mode and opens a prefilled email instead, so the
   call to action still completes without a backend or any secret in the repo. */
const LEAD_ENDPOINT = ""; // e.g. "https://your-form-provider.example/submit"
const LEAD_EMAIL = "hello@room39.example"; // placeholder for preview

(function () {
  "use strict";

  /* ----- Scroll reveals ----- */
  const reveals = document.querySelectorAll(".reveal");
  if ("IntersectionObserver" in window) {
    const io = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add("in");
            io.unobserve(entry.target);
          }
        });
      },
      { rootMargin: "0px 0px -8% 0px", threshold: 0.12 }
    );
    reveals.forEach((el, i) => {
      el.style.transitionDelay = Math.min(i % 4, 3) * 60 + "ms";
      io.observe(el);
    });
  } else {
    reveals.forEach((el) => el.classList.add("in"));
  }

  /* ----- Plan selection ----- */
  const form = document.getElementById("lead-form");
  const interest = document.getElementById("interest");
  const leadSection = document.getElementById("lead");

  document.querySelectorAll("[data-plan]").forEach((btn) => {
    btn.addEventListener("click", () => {
      const plan = btn.getAttribute("data-plan");
      if (interest && plan) {
        // Map the button's plan text onto the closest <option>.
        const match = Array.from(interest.options).find((o) =>
          o.value.toLowerCase().includes(plan.split(" (")[0].toLowerCase().slice(0, 12))
        );
        interest.value = match ? match.value : plan;
      }
      if (leadSection) {
        leadSection.scrollIntoView({ behavior: "smooth", block: "start" });
        const first = document.getElementById("name");
        if (first) window.setTimeout(() => first.focus({ preventScroll: true }), 650);
      }
    });
  });

  /* ----- Form validation + submit ----- */
  if (!form) return;

  const fields = ["name", "clinic", "email", "city"].map((id) => document.getElementById(id));
  const errorBox = document.getElementById("form-error");
  const successPanel = document.getElementById("lead-success");
  const successPlan = document.getElementById("success-plan");
  const leadWrap = document.querySelector(".lead-wrap");

  const emailOk = (v) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v.trim());

  fields.forEach((field) => {
    if (!field) return;
    field.addEventListener("input", () => field.classList.remove("invalid"));
  });

  function validate() {
    let ok = true;
    fields.forEach((field) => {
      if (!field) return;
      const value = field.value.trim();
      const valid = field.id === "email" ? emailOk(value) : value.length > 0;
      field.classList.toggle("invalid", !valid);
      if (!valid) ok = false;
    });
    return ok;
  }

  function payload() {
    return {
      name: document.getElementById("name").value.trim(),
      clinic: document.getElementById("clinic").value.trim(),
      email: document.getElementById("email").value.trim(),
      website: document.getElementById("website").value.trim(),
      city: document.getElementById("city").value.trim(),
      treatments: document.getElementById("treatments").value.trim(),
      interest: interest ? interest.value : "",
      page: "room39-one-pager",
      submittedAt: new Date().toISOString(),
    };
  }

  function showSuccess(planLabel) {
    if (successPlan && planLabel) successPlan.textContent = planLabel;
    form.hidden = true;
    if (successPanel) successPanel.hidden = false;
    if (leadWrap) leadWrap.classList.add("success");
  }

  function openMailFallback(data) {
    const subject = "AI Visibility Snapshot request — " + (data.clinic || data.name);
    const body = [
      "Name: " + data.name,
      "Clinic: " + data.clinic,
      "Email: " + data.email,
      "Website: " + (data.website || "—"),
      "City: " + data.city,
      "Treatments: " + (data.treatments || "—"),
      "Interest: " + data.interest,
    ].join("\n");
    window.location.href =
      "mailto:" + LEAD_EMAIL + "?subject=" + encodeURIComponent(subject) + "&body=" + encodeURIComponent(body);
  }

  form.addEventListener("submit", function (event) {
    event.preventDefault();
    if (errorBox) errorBox.hidden = true;

    if (!validate()) {
      if (errorBox) errorBox.hidden = false;
      const firstInvalid = fields.find((f) => f && f.classList.contains("invalid"));
      if (firstInvalid) firstInvalid.focus();
      return;
    }

    const data = payload();
    const button = document.getElementById("submit-btn");
    if (button) {
      button.disabled = true;
      button.querySelector("span").textContent = "Sending…";
    }

    const finish = () => showSuccess(data.interest);

    if (LEAD_ENDPOINT && typeof fetch === "function") {
      fetch(LEAD_ENDPOINT, {
        method: "POST",
        headers: { "Content-Type": "application/json", Accept: "application/json" },
        body: JSON.stringify(data),
      })
        .then(() => finish())
        .catch(() => {
          // Never strand the visitor: fall back to email, then confirm.
          openMailFallback(data);
          finish();
        });
    } else {
      openMailFallback(data);
      finish();
    }
  });
})();
