/* Room 39 — one-page offer site behavior
   - scroll-reveal via IntersectionObserver (transform/opacity only)
   - plan buttons preselect the form's "interest" field and scroll to it
   - lead form validation + real submission to a free form backend

   LEAD CAPTURE
   ------------
   The form POSTs to a free serverless form backend (no server, no secret).

   Selected backend: FormSubmit.co (free, no signup). Set LEAD_ENDPOINT to
   "https://formsubmit.co/ajax/<business-inbox>" and leave LEAD_ACCESS_KEY empty.
   The destination address is the only value, and it is already public on the
   site's contact page, so nothing secret ships in this static file.

   Web3Forms is also supported: set LEAD_ENDPOINT to
   "https://api.web3forms.com/submit" and paste the *public* access key. That key
   can only deliver mail to the form owner's inbox, so it is safe to ship too.

   The success panel is shown ONLY after the backend returns a real 2xx success.
   Every other outcome (network error, non-2xx, disabled key) shows a visible
   error with a mailto fallback so a lead is never told "received" when it was
   not. */
const LEAD_ENDPOINT = "https://api.web3forms.com/submit";
const LEAD_ACCESS_KEY = ""; // public Web3Forms access key — leave empty for URL-keyed backends (Formspree/FormSubmit)
const LEAD_EMAIL = "hello@room39.example"; // shown to visitors only if the submit fails

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
  const button = document.getElementById("submit-btn");
  const buttonLabel = button ? button.querySelector("span") : null;

  const VALIDATION_MESSAGE = "Please add your name, clinic, a valid work email, and a city.";
  const DEFAULT_ERROR_MESSAGE =
    "Sorry — we could not send your request just now. Please try again, or email us directly.";

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

  function showError(message) {
    if (!errorBox) return;
    errorBox.textContent = message;
    errorBox.hidden = false;
  }

  function clearError() {
    if (errorBox) errorBox.hidden = true;
  }

  function setSending(isSending) {
    if (!button) return;
    button.disabled = isSending;
    button.setAttribute("aria-busy", isSending ? "true" : "false");
    if (buttonLabel) buttonLabel.textContent = isSending ? "Sending…" : "Request my snapshot";
  }

  function showSuccess(planLabel) {
    if (successPlan && planLabel) successPlan.textContent = planLabel;
    form.hidden = true;
    if (successPanel) successPanel.hidden = false;
    if (leadWrap) leadWrap.classList.add("success");
  }

  function failureMessage(status, providerMessage) {
    if (status === 0) {
      return "We could not reach the server. Check your connection and try again, or email us directly.";
    }
    if (status === 429) {
      return "We are getting a lot of requests right now. Please try again in a minute, or email us directly.";
    }
    if (providerMessage) return providerMessage;
    return DEFAULT_ERROR_MESSAGE;
  }

  form.addEventListener("submit", function (event) {
    event.preventDefault();
    clearError();

    if (!validate()) {
      showError(VALIDATION_MESSAGE);
      const firstInvalid = fields.find((f) => f && f.classList.contains("invalid"));
      if (firstInvalid) firstInvalid.focus();
      return;
    }

    const data = payload();

    if (!LEAD_ENDPOINT || (LEAD_ENDPOINT.indexOf("web3forms.com") !== -1 && !LEAD_ACCESS_KEY) || typeof fetch !== "function") {
      // Capture is not configured. Never fake success — a lost lead must be visible.
      showError(DEFAULT_ERROR_MESSAGE);
      return;
    }

    setSending(true);

    var isFormSubmit = LEAD_ENDPOINT.indexOf("formsubmit.co") !== -1;
    var body;
    if (LEAD_ACCESS_KEY) {
      body = Object.assign({ access_key: LEAD_ACCESS_KEY, subject: "New AI Visibility Snapshot request", from_name: "Room 39 site" }, data);
    } else if (isFormSubmit) {
      // FormSubmit control fields: no captcha (AJAX), readable table, clear subject.
      body = Object.assign({ _subject: "New AI Visibility Snapshot request", _template: "table", _captcha: "false" }, data);
    } else {
      body = data;
    }

    fetch(LEAD_ENDPOINT, {
      method: "POST",
      headers: { "Content-Type": "application/json", Accept: "application/json" },
      body: JSON.stringify(body),
    })
      .then(function (response) {
        return response
          .json()
          .catch(function () {
            return {};
          })
          .then(function (body) {
            var ok = response.ok && body && body.success !== false;
            if (!ok) {
              throw { status: response.status, message: body && body.message };
            }
            showSuccess(data.interest);
          });
      })
      .catch(function (err) {
        setSending(false);
        var status = err && typeof err.status === "number" ? err.status : 0;
        showError(failureMessage(status, err && err.message));
        if (errorBox && LEAD_EMAIL && LEAD_EMAIL.indexOf(".example") === -1) {
          errorBox.innerHTML += ' Or email <a href="mailto:' + LEAD_EMAIL + '">' + LEAD_EMAIL + "</a>.";
        }
      });
  });
})();
