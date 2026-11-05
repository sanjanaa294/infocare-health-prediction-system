/**
 * HealthCare AI Prediction & Patient Management Frontend JavaScript
 * Handles REST API interactions, UI updates, validations, modals, and test case auto-fill.
 */

// Assessment Test Cases exact data
const ASSESSMENT_TEST_CASES = [
  {
    testId: 1,
    name: "Robyn Pears",
    dob: "28.01.1960",
    email: "robyn@gmail.com",
    glucose: 232,
    haemoglobin: 13.5,
    cholesterol: 180,
    expected: "Valid. Record should be saved successfully with AI remarks.",
    expectedStatus: "valid"
  },
  {
    testId: 2,
    name: "John Hunter",
    dob: "10.12.1990",
    email: "hunter@gmail",
    glucose: 94,
    haemoglobin: 15,
    cholesterol: 200,
    expected: "Reject because 'hunter@gmail' is an invalid email address (missing domain extension).",
    expectedStatus: "invalid"
  },
  {
    testId: 3,
    name: "Darryl Tim",
    dob: "12.11.1993",
    email: "timd@smh.com.au",
    glucose: 240,
    haemoglobin: 18.6,
    cholesterol: 326,
    expected: "Valid. Record should be saved successfully with AI remarks.",
    expectedStatus: "valid"
  },
  {
    testId: 4,
    name: "Peter Larry",
    dob: "31.11.2001",
    email: "Larry@hotmail.com",
    glucose: 88,
    haemoglobin: 11.5,
    cholesterol: 165,
    expected: "Reject because 31.11.2001 is not a valid calendar date (November has only 30 days).",
    expectedStatus: "invalid"
  },
  {
    testId: 5,
    name: "Sam Kerr",
    dob: "09.12.2006",
    email: "sam@news.com.au",
    glucose: 198,
    haemoglobin: 8.9,
    cholesterol: 192,
    expected: "Valid. Record should be saved successfully with AI remarks.",
    expectedStatus: "valid"
  },
  {
    testId: 6,
    name: "Robyn Pears",
    dob: "28.01.1960",
    email: "robyn@gmail.com",
    glucose: 232,
    haemoglobin: 13.5,
    cholesterol: 180,
    expected: "Valid. Must be saved as a separate record despite being a duplicate of Test 1.",
    expectedStatus: "valid"
  },
  {
    testId: 7,
    name: "Madison XI",
    dob: "12.09.1998",
    email: "madison@hotmail.com",
    glucose: 85,
    haemoglobin: 7.6,
    cholesterol: 163,
    expected: "Valid. Record should be saved successfully with AI remarks.",
    expectedStatus: "valid"
  },
  {
    testId: 8,
    name: "Kris Wu",
    dob: "19.10.2030",
    email: "Kris.wu.gmail.com",
    glucose: 79,
    haemoglobin: 16.5,
    cholesterol: 197,
    expected: "Reject because date of birth is in the future (2030) and email is invalid (no @).",
    expectedStatus: "invalid"
  },
  {
    testId: 9,
    name: "Tenille Singh",
    dob: "30.11.1991",
    email: "Tenille@yahoo.com",
    glucose: 101,
    haemoglobin: 15,
    cholesterol: 310,
    expected: "Valid. Record should be saved successfully with AI remarks.",
    expectedStatus: "valid"
  },
  {
    testId: 10,
    name: "Prem Kumar",
    dob: "28.04.1990",
    email: "prem@telstra.com",
    glucose: 155,
    haemoglobin: 12.5,
    cholesterol: 265,
    expected: "Valid. Record should be saved successfully with AI remarks.",
    expectedStatus: "valid"
  }
];

// Show Toast Notification
function showToast(title, message, type = "success") {
  const container = document.getElementById("toastContainer");
  if (!container) return;

  const bgClass = type === "success" ? "bg-success" : type === "error" ? "bg-danger" : "bg-warning";
  const icon = type === "success" ? "bi-check-circle" : type === "error" ? "bi-exclamation-octagon" : "bi-exclamation-triangle";

  const toastEl = document.createElement("div");
  toastEl.className = `toast align-items-center text-white ${bgClass} border-0 mb-2`;
  toastEl.setAttribute("role", "alert");
  toastEl.setAttribute("aria-live", "assertive");
  toastEl.setAttribute("aria-atomic", "true");

  toastEl.innerHTML = `
    <div class="d-flex">
      <div class="toast-body d-flex align-items-center gap-2">
        <i class="bi ${icon} fs-5"></i>
        <div>
          <strong>${title}</strong><br>
          <small>${message}</small>
        </div>
      </div>
      <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
    </div>
  `;

  container.appendChild(toastEl);
  const bsToast = new bootstrap.Toast(toastEl, { delay: 5000 });
  bsToast.show();
  toastEl.addEventListener("hidden.bs.toast", () => toastEl.remove());
}

// Show/Hide Global Loading Overlay
function showLoading(message = "Analyzing blood biomarkers with OpenRouter AI... Please wait.") {
  let overlay = document.getElementById("loadingOverlay");
  if (!overlay) {
    overlay = document.createElement("div");
    overlay.id = "loadingOverlay";
    overlay.className = "loading-overlay";
    overlay.innerHTML = `
      <div class="pulse-spinner mb-3"></div>
      <h5 class="fw-bold mb-1" id="loadingTitle">Processing Patient Record</h5>
      <p class="text-light text-center px-3" id="loadingText">${message}</p>
    `;
    document.body.appendChild(overlay);
  } else {
    document.getElementById("loadingText").innerText = message;
    overlay.style.display = "flex";
  }
}

function hideLoading() {
  const overlay = document.getElementById("loadingOverlay");
  if (overlay) {
    overlay.style.display = "none";
  }
}

// Quick-fill assessment test case into the Add Patient form
function loadAssessmentCase(testIndex) {
  const testCase = ASSESSMENT_TEST_CASES[testIndex - 1];
  if (!testCase) return;

  const nameInput = document.getElementById("full_name");
  const dobInput = document.getElementById("date_of_birth");
  const emailInput = document.getElementById("email");
  const glucoseInput = document.getElementById("glucose");
  const haemoglobinInput = document.getElementById("haemoglobin");
  const cholesterolInput = document.getElementById("cholesterol");

  if (nameInput) nameInput.value = testCase.name;
  if (dobInput) dobInput.value = testCase.dob;
  if (emailInput) emailInput.value = testCase.email;
  if (glucoseInput) glucoseInput.value = testCase.glucose;
  if (haemoglobinInput) haemoglobinInput.value = testCase.haemoglobin;
  if (cholesterolInput) cholesterolInput.value = testCase.cholesterol;

  const infoBox = document.getElementById("selectedTestCaseInfo");
  if (infoBox) {
    infoBox.style.display = "block";
    infoBox.innerHTML = `
      <div class="alert ${testCase.expectedStatus === 'valid' ? 'alert-info' : 'alert-warning'} mb-0">
        <strong>Loaded Test Case ${testCase.testId}: ${testCase.name}</strong><br>
        <small><strong>Expected Result:</strong> ${testCase.expected}</small>
      </div>
    `;
  }
}

// Handle Add Patient Form Submission
document.addEventListener("DOMContentLoaded", () => {
  const addForm = document.getElementById("addPatientForm");
  if (addForm) {
    addForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      const errorAlert = document.getElementById("formErrorAlert");
      if (errorAlert) errorAlert.style.display = "none";

      const payload = {
        full_name: document.getElementById("full_name").value,
        date_of_birth: document.getElementById("date_of_birth").value,
        email: document.getElementById("email").value,
        glucose: document.getElementById("glucose").value,
        haemoglobin: document.getElementById("haemoglobin").value,
        cholesterol: document.getElementById("cholesterol").value,
      };

      showLoading("Sending blood test metrics to OpenRouter AI & creating record...");

      try {
        const response = await fetch("/api/patients", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload),
        });

        const data = await response.json();
        hideLoading();

        if (response.ok) {
          showToast("Success", `Patient ${data.full_name} was saved successfully!`, "success");
          setTimeout(() => {
            window.location.href = "/patients";
          }, 1200);
        } else {
          // Backend validation error (422 or other)
          let errorMsg = "Validation failed.";
          if (data.detail) {
            if (Array.isArray(data.detail)) {
              errorMsg = data.detail.join("<br>");
            } else {
              errorMsg = data.detail;
            }
          } else if (data.message) {
            errorMsg = data.message;
          }

          if (errorAlert) {
            errorAlert.innerHTML = `
              <div class="d-flex align-items-start gap-2">
                <i class="bi bi-x-circle-fill text-danger fs-5 mt-1"></i>
                <div>
                  <strong>Submission Rejected (Validation Error):</strong><br>
                  <span>${errorMsg}</span>
                </div>
              </div>
            `;
            errorAlert.style.display = "block";
            errorAlert.scrollIntoView({ behavior: "smooth", block: "start" });
          }
          showToast("Validation Error", "Please review the highlighted errors.", "error");
        }
      } catch (err) {
        hideLoading();
        if (errorAlert) {
          errorAlert.innerHTML = `<strong>Network Error:</strong> ${err.message}`;
          errorAlert.style.display = "block";
        }
        showToast("Error", "Could not connect to server.", "error");
      }
    });
  }

  // Handle Edit Patient Form Submission
  const editForm = document.getElementById("editPatientForm");
  if (editForm) {
    editForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      const patientId = editForm.dataset.patientId;
      const errorAlert = document.getElementById("editFormErrorAlert");
      if (errorAlert) errorAlert.style.display = "none";

      const payload = {
        full_name: document.getElementById("full_name").value,
        date_of_birth: document.getElementById("date_of_birth").value,
        email: document.getElementById("email").value,
        glucose: document.getElementById("glucose").value,
        haemoglobin: document.getElementById("haemoglobin").value,
        cholesterol: document.getElementById("cholesterol").value,
      };

      showLoading("Updating patient record and checking for AI remarks regeneration...");

      try {
        const response = await fetch(`/api/patients/${patientId}`, {
          method: "PUT",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload),
        });

        const data = await response.json();
        hideLoading();

        if (response.ok) {
          showToast("Updated", `Patient ${data.full_name} updated successfully!`, "success");
          setTimeout(() => {
            window.location.href = "/patients";
          }, 1200);
        } else {
          let errorMsg = "Update failed.";
          if (data.detail) {
            if (Array.isArray(data.detail)) {
              errorMsg = data.detail.join("<br>");
            } else {
              errorMsg = data.detail;
            }
          }
          if (errorAlert) {
            errorAlert.innerHTML = `<strong>Error:</strong> ${errorMsg}`;
            errorAlert.style.display = "block";
          }
          showToast("Error", "Validation failed during update.", "error");
        }
      } catch (err) {
        hideLoading();
        showToast("Error", err.message, "error");
      }
    });
  }

  // Search input handler
  const searchInput = document.getElementById("patientSearchInput");
  if (searchInput) {
    searchInput.addEventListener("input", (e) => {
      const query = e.target.value.toLowerCase().trim();
      const rows = document.querySelectorAll(".patient-row");
      rows.forEach((row) => {
        const name = row.dataset.name ? row.dataset.name.toLowerCase() : "";
        const email = row.dataset.email ? row.dataset.email.toLowerCase() : "";
        const id = row.dataset.id ? row.dataset.id.toLowerCase() : "";
        if (name.includes(query) || email.includes(query) || id.includes(query)) {
          row.style.display = "";
        } else {
          row.style.display = "none";
        }
      });
    });
  }
});

// Open Patient View Modal
async function viewPatientDetails(patientId) {
  try {
    const res = await fetch(`/api/patients/${patientId}`);
    if (!res.ok) throw new Error("Patient not found");
    const p = await res.json();

    document.getElementById("modalPatientName").innerText = p.full_name;
    document.getElementById("modalPatientId").innerText = `#${p.id}`;
    document.getElementById("modalDob").innerText = p.date_of_birth;
    document.getElementById("modalEmail").innerText = p.email;
    document.getElementById("modalGlucose").innerText = `${p.glucose} mg/dL`;
    document.getElementById("modalHaemoglobin").innerText = `${p.haemoglobin} g/dL`;
    document.getElementById("modalCholesterol").innerText = `${p.cholesterol} mg/dL`;
    document.getElementById("modalRemarks").innerText = p.remarks || "No remarks generated yet.";
    document.getElementById("modalAiStatus").innerText = p.ai_status;

    const statusBadge = document.getElementById("modalAiStatusBadge");
    if (p.ai_status === "COMPLETED") {
      statusBadge.className = "badge-ai-completed";
      statusBadge.innerHTML = '<i class="bi bi-check-circle-fill"></i> Completed';
    } else if (p.ai_status === "FAILED") {
      statusBadge.className = "badge-ai-failed";
      statusBadge.innerHTML = '<i class="bi bi-exclamation-circle-fill"></i> Failed';
    } else {
      statusBadge.className = "badge-ai-pending";
      statusBadge.innerHTML = '<i class="bi bi-clock-fill"></i> Pending';
    }

    const editBtn = document.getElementById("modalEditBtn");
    if (editBtn) editBtn.href = `/patients/edit/${p.id}`;

    const regenBtn = document.getElementById("modalRegenBtn");
    if (regenBtn) {
      regenBtn.onclick = () => regenerateRemarks(p.id, true);
    }

    const modal = new bootstrap.Modal(document.getElementById("patientDetailModal"));
    modal.show();
  } catch (err) {
    showToast("Error", err.message, "error");
  }
}

// Trigger Delete Confirmation Modal
let patientIdToDelete = null;
function confirmDeletePatient(id, name) {
  patientIdToDelete = id;
  const nameEl = document.getElementById("deletePatientName");
  if (nameEl) nameEl.innerText = name;
  const modal = new bootstrap.Modal(document.getElementById("deleteConfirmModal"));
  modal.show();
}

async function executeDeletePatient() {
  if (!patientIdToDelete) return;
  try {
    const res = await fetch(`/api/patients/${patientIdToDelete}`, {
      method: "DELETE",
    });

    if (res.ok) {
      showToast("Deleted", "Patient record deleted successfully.", "success");
      const modalEl = document.getElementById("deleteConfirmModal");
      const modal = bootstrap.Modal.getInstance(modalEl);
      if (modal) modal.hide();

      // Remove row if exists
      const row = document.getElementById(`patient-row-${patientIdToDelete}`);
      if (row) {
        row.remove();
      } else {
        setTimeout(() => window.location.reload(), 800);
      }
    } else {
      const data = await res.json();
      showToast("Error", data.detail || "Could not delete patient.", "error");
    }
  } catch (err) {
    showToast("Error", err.message, "error");
  } finally {
    patientIdToDelete = null;
  }
}

// Regenerate AI Remarks
async function regenerateRemarks(patientId, isFromModal = false) {
  showLoading("Contacting OpenRouter AI API to analyze blood markers...");
  try {
    const res = await fetch(`/api/patients/${patientId}/generate-remarks`, {
      method: "POST",
    });

    const data = await res.json();
    hideLoading();

    if (res.ok) {
      showToast("AI Remarks Updated", `Status: ${data.ai_status}`, data.ai_status === "COMPLETED" ? "success" : "warning");
      if (isFromModal) {
        document.getElementById("modalRemarks").innerText = data.remarks;
        const statusBadge = document.getElementById("modalAiStatusBadge");
        if (data.ai_status === "COMPLETED") {
          statusBadge.className = "badge-ai-completed";
          statusBadge.innerHTML = '<i class="bi bi-check-circle-fill"></i> Completed';
        } else {
          statusBadge.className = "badge-ai-failed";
          statusBadge.innerHTML = '<i class="bi bi-exclamation-circle-fill"></i> Failed';
        }
      }
      setTimeout(() => window.location.reload(), 1000);
    } else {
      showToast("Error", data.detail || "Could not regenerate remarks.", "error");
    }
  } catch (err) {
    hideLoading();
    showToast("Error", err.message, "error");
  }
}

