const form = document.querySelector("#goal-form");
const startButton = document.querySelector("#start");
const stopButton = document.querySelector("#stop");
const message = document.querySelector("#message");
const distance = document.querySelector("#distance");
const averagePace = document.querySelector("#average-pace");
const requiredPace = document.querySelector("#required-pace");
const elapsedTime = document.querySelector("#elapsed-time");
const targetTimePassed = document.querySelector("#target-time-passed");

const previewButton = document.querySelector("#preview-plan");
const planMessage = document.querySelector("#plan-message");
const splitPlan = document.querySelector("#split-plan");
const splitList = document.querySelector("#split-list");

const paceStatus = document.querySelector("#pace-status");

const paceStatuses = {
  ahead: { label: "Ahead", tone: "green" },
  on_plan: { label: "On plan", tone: "green" },
  behind: { label: "Behind", tone: "red" },
  goal_reached: { label: "Goal reached", tone: "green" },
  goal_missed: { label: "Goal missed", tone: "red" },
  waiting: { label: "Waiting for movement", tone: "neutral" },
  finished: { label: "Run finished", tone: "neutral" }
};

function setPaceStatus(status) {
  const { label, tone } = paceStatuses[status] ?? paceStatuses.waiting;

  if (paceStatus.textContent !== label) {
    paceStatus.textContent = label;
  }

  paceStatus.dataset.tone = tone;
}

function readGoal() {
  const fields = new FormData(form);

  return {
    goal_distance_km: Number(fields.get("distance")),
    goal_time_minutes: Number(fields.get("minutes"))
  };
}

function formatSplitTime(decimalMinutes) {
  const totalSeconds = Math.round(decimalMinutes * 60);
  const minutes = Math.floor(totalSeconds / 60);
  const seconds = String(totalSeconds % 60).padStart(2, "0");

  return `${minutes}:${seconds}`;
}

const runMap = L.map("run-map").setView([0, 0], 2);

L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
  maxZoom: 19,
  attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
}).addTo(runMap);

const routeLine = L.polyline([], {
  color: "#2563eb",
  weight: 4
}).addTo(runMap);

let runnerMarker = null;

function drawRoutePoint(latitude, longitude) {
    const position = [latitude, longitude];
  
    routeLine.addLatLng(position);
  
    if (runnerMarker === null) {
      runnerMarker = L.circleMarker(position, {
        radius: 6,
        color: "#ffffff",
        weight: 2,
        fillColor: "#2563eb",
        fillOpacity: 1
      }).addTo(runMap);
  
      runMap.setView(position, 16);
      return;
    }
  
    runnerMarker.setLatLng(position);
  
    if (!runMap.getBounds().contains(position)) {
      runMap.panTo(position);
    }
  }
  
  function resetRoute() {
    routeLine.setLatLngs([]);
  
    if (runnerMarker !== null) {
      runnerMarker.remove();
      runnerMarker = null;
    }
  }

let activeRun = null;
let timerId = null;

function stopTimer() {
    clearInterval(timerId);
    timerId = null;
  }
  
function startTimer(startedAt, goalMinutes) {
    stopTimer();
  
    const startedAtMs = Date.parse(startedAt);
    const targetMs = goalMinutes * 60_000;
  
    function updateTimer() {
      const elapsedMs = Math.max(0, Date.now() - startedAtMs);
      const totalSeconds = Math.floor(elapsedMs / 1000);
      const minutes = String(Math.floor(totalSeconds / 60)).padStart(2, "0");
      const seconds = String(totalSeconds % 60).padStart(2, "0");
      const overTarget = elapsedMs >= targetMs;
  
      elapsedTime.textContent = `${minutes}:${seconds}`;
      elapsedTime.classList.toggle("over-target", overTarget);
      targetTimePassed.hidden = !overTarget;
    }
  
    updateTimer();
    timerId = setInterval(updateTimer, 250);
}

async function postJson(url, body) {
  const response = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body)
  });

  if (!response.ok) {
    throw new Error(`${url} returned HTTP ${response.status}`);
  }

  return response.json();
}

function formatPace(minutesPerKm) {
  if (!Number.isFinite(minutesPerKm)) return "—";

  const totalSeconds = Math.round(minutesPerKm * 60);
  const minutes = Math.floor(totalSeconds / 60);
  const seconds = String(totalSeconds % 60).padStart(2, "0");
  return `${minutes}:${seconds}/km`;
}

async function sendPoint(run, { coords, timestamp }) {
  if (activeRun !== run || run.sending || timestamp - run.lastSentAt < 3000) {
    return;
  }

  run.sending = true;
  run.lastSentAt = timestamp;

  try {
    const update = await postJson(`/runs/${run.id}/points`, {
      latitude: coords.latitude,
      longitude: coords.longitude,
      accuracy_m: coords.accuracy,
      recorded_at: new Date(timestamp).toISOString()
    });

    if (activeRun !== run) return;

    drawRoutePoint(coords.latitude, coords.longitude);

    if (run.stopping) return;

    distance.textContent = `${update.distance_km.toFixed(3)} km`;
    averagePace.textContent = formatPace(update.progress.average_pace_min_per_km);
    requiredPace.textContent = formatPace(update.progress.required_pace_min_per_km);
    message.textContent = "Tracking your run.";
    const status = update.progress.status;

    if (update.distance_km === 0 && status !== "goal_missed") {
    setPaceStatus("waiting");
    } else {
    setPaceStatus(status);
    }
  } catch (error) {
    if (activeRun === run) message.textContent = error.message;
  } finally {
    run.sending = false;
  }
}

form.addEventListener("submit", async event => {
  event.preventDefault();
  startButton.disabled = true;
  message.textContent = "Starting run…";

  try {
    if (!navigator.geolocation) {
      throw new Error("Location is unavailable on this page.");
    }

    const goal = new FormData(form);
    const goalMinutes = Number(goal.get("minutes"));
    const { id, started_at: startedAt } = await postJson("/runs", {
      goal_distance_km: Number(goal.get("distance")),
      goal_time_minutes: goalMinutes
    });

    const run = { id, goalMinutes, lastSentAt: -Infinity, sending: false };

    run.watchId = navigator.geolocation.watchPosition(
      point => {
            if (run.stopping || run.sending) return;
            run.pendingPoint = sendPoint(run, point);
          },
      error => {
        if (activeRun === run) message.textContent = `Location: ${error.message}`;
      },
      { enableHighAccuracy: true, maximumAge: 0, timeout: 15000 }
    );

    activeRun = run;
    resetRoute();
    startTimer(startedAt, goalMinutes);
    distance.textContent = "0.000 km";
    averagePace.textContent = "—";
    requiredPace.textContent = "—";
    setPaceStatus("waiting");
    message.textContent = "Waiting for your first location…";
    stopButton.disabled = false;
  } catch (error) {
    startButton.disabled = false;
    message.textContent = error.message;
  }
});

stopButton.addEventListener("click", async () => {
    const run = activeRun;
    if (!run) return;
  
    run.stopping = true;
    stopButton.disabled = true;
    navigator.geolocation.clearWatch(run.watchId);
    stopTimer();
    message.textContent = "Saving your run…";
  
    try {
      await run.pendingPoint;
  
      const summary = await postJson(`/runs/${run.id}/finish`, {});
  
      distance.textContent = `${summary.distance_km.toFixed(3)} km`;
      averagePace.textContent = formatPace(summary.average_pace_min_per_km);
      requiredPace.textContent = "—";
  
      const totalSeconds = Math.floor(summary.elapsed_time_minutes * 60);
      const minutes = String(Math.floor(totalSeconds / 60)).padStart(2, "0");
      const seconds = String(totalSeconds % 60).padStart(2, "0");
      const overTarget = summary.elapsed_time_minutes >= run.goalMinutes;
  
      elapsedTime.textContent = `${minutes}:${seconds}`;
      elapsedTime.classList.toggle("over-target", overTarget);
      targetTimePassed.hidden = !overTarget;
  
      setPaceStatus("finished");
      activeRun = null;
      startButton.disabled = false;
      message.textContent = summary.distance_km === 0
        ? "Run saved. No distance was recorded."
        : "Run finished.";
    } catch (error) {
      stopButton.disabled = false;
      message.textContent = `Could not save the finish. Tap Stop to retry. ${error.message}`;
    }
  });

  let goalVersion = 0;

form.addEventListener("input", () => {
  goalVersion += 1;
  splitPlan.hidden = true;
  planMessage.textContent = "";
});

previewButton.addEventListener("click", async () => {
  if (!form.reportValidity()) return;

  const version = goalVersion;
  previewButton.disabled = true;
  splitPlan.hidden = true;
  planMessage.textContent = "Calculating splits…";

  try {
    const { splits } = await postJson("/pace/plan", readGoal());

    if (version !== goalVersion) return;

    const items = splits.map(split => {
      const item = document.createElement("li");
      const time = formatSplitTime(split.time_elapsed_minutes);
      item.textContent = `${split.distance_km} km · ${time}`;
      return item;
    });

    splitList.replaceChildren(...items);
    splitPlan.hidden = false;
    planMessage.textContent = "";
  } catch (error) {
    if (version === goalVersion) {
      planMessage.textContent = `Could not load the plan. ${error.message}`;
    }
  } finally {
    previewButton.disabled = false;
  }
});