const recordButton = document.getElementById("recordButton");
const status = document.getElementById("status");
const statusIndicator = document.getElementById("statusIndicator");
const statusDot = document.getElementById("statusDot");
const result = document.getElementById("result");
const intent = document.getElementById("intent");
const entities = document.getElementById("entities");
const command = document.getElementById("command");
const searchResults = document.getElementById("searchResults");



let audioContext;
let source;
let processor;
let stream;
let audioData = [];
let isRecording = false;


// Start / Stop recording
recordButton.addEventListener("click", async () => {

    if (!isRecording) {
        await startRecording();
    } else {
        stopRecording();
    }

});


// Start recording
async function startRecording() {

    try {

        stream = await navigator.mediaDevices.getUserMedia({
            audio: true
        });

        audioContext = new AudioContext();

        source = audioContext.createMediaStreamSource(stream);

        processor = audioContext.createScriptProcessor(
            4096,
            1,
            1
        );

        audioData = [];

        processor.onaudioprocess = (event) => {

            const channelData =
                event.inputBuffer.getChannelData(0);

            audioData.push(
                new Float32Array(channelData)
            );
        };

        source.connect(processor);
        processor.connect(audioContext.destination);

        isRecording = true;

        recordButton.textContent = "⏹ Stop Recording";
        setStatus("Listening... Speak now!", "listening");
        result.textContent = "";

    } catch (error) {

        console.error(error);

        status.textContent =
            "Could not access microphone.";

    }
}


// Stop recording
async function stopRecording() {

    isRecording = false;

    processor.disconnect();
    source.disconnect();

    stream.getTracks().forEach(track => {
        track.stop();
    });

    const wavBlob = createWavFile(
        audioData,
        audioContext.sampleRate
    );

    recordButton.disabled = true;
    recordButton.textContent = "Processing...";
    setStatus("Processing...", "processing");

    try {

        const formData = new FormData();

        formData.append(
            "file",
            wavBlob,
            "recording.wav"
        );

        const response = await fetch(
            "https://veyravoice.onrender.com/voice",
            {
                method: "POST",
                body: formData
            }
        );

        const data = await response.json();

        if (data.success) {
            

            result.textContent = data.text;
            intent.textContent = data.intent;
            entities.textContent = JSON.stringify(data.entities);
        if (data.confirmation_required) {

            command.textContent = data.confirmation_message;

            speak(data.confirmation_message);

        } else {

            let message = data.command?.message || "";

            if (data.command?.snags) {

                const count = data.command.snags.length;

                if (count === 0) {

                    message = "I couldn't find any matching snags.";

                } else if (count === 1) {

                    message = "I found 1 snag.";

                } else {

                    message = `I found ${count} snags.`;

                }
            }

            command.textContent = message;

            speak(message);

        }

            searchResults.innerHTML = "";


            // --------------------------------
            // Search results
            // --------------------------------

            if (data.command?.snags) {

                if (data.command.snags.length === 0) {

                    searchResults.textContent =
                        "No snags found.";

                } else {

                    const heading =
                        document.createElement("h3");

                    heading.textContent =
                        `Search Results (${data.command.count})`;

                    searchResults.appendChild(heading);

                    data.command.snags.forEach(
                        (snag, index) => {

                            const snagElement =
                                document.createElement("div");

                            snagElement.innerHTML = `
                                <p>
                                    <strong>Snag ${index + 1}</strong><br>
                                    Location:
                                    ${snag.location || "N/A"}<br>

                                    Issue:
                                    ${snag.issue || "N/A"}<br>

                                    Assignee:
                                    ${snag.assignee || "N/A"}<br>

                                    Status:
                                    ${snag.status || "N/A"}
                                </p>
                            `;

                            searchResults.appendChild(
                                snagElement
                            );
                        }
                    );
                }
            }


            // --------------------------------
            // Delete candidates
            // --------------------------------

            if (data.command?.matches) {

                const matches =
                    data.command.matches;

                const heading =
                    document.createElement("h3");

                heading.textContent =
                    `Matching Snags (${matches.length})`;

                searchResults.appendChild(
                    heading
                );


                matches.forEach(
                    (snag, index) => {

                        const snagElement =
                            document.createElement("div");

                        snagElement.innerHTML = `
                            <p>
                                <strong>
                                    Snag ${index + 1}
                                </strong><br>

                                Location:
                                ${snag.location || "N/A"}<br>

                                Issue:
                                ${snag.issue || "N/A"}<br>

                                Assignee:
                                ${snag.assignee || "N/A"}<br>

                                Status:
                                ${snag.status || "N/A"}
                            </p>
                        `;

                        searchResults.appendChild(
                            snagElement
                        );
                    }
                );
            }

            setStatus("Done!", "done");
        } else {

            status.textContent =
                "Speech recognition failed.";

        }

    } catch (error) {

        console.error(error);

        status.textContent =
            "Could not connect to server.";

    }

    recordButton.disabled = false;
    recordButton.textContent = " Start Recording";

    await audioContext.close();
}


// Create WAV file
function createWavFile(audioData, sampleRate) {

    let totalLength = 0;

    for (const chunk of audioData) {
        totalLength += chunk.length;
    }

    const samples = new Float32Array(totalLength);

    let offset = 0;

    for (const chunk of audioData) {

        samples.set(chunk, offset);

        offset += chunk.length;
    }

    const buffer =
        new ArrayBuffer(44 + samples.length * 2);

    const view = new DataView(buffer);

    writeString(view, 0, "RIFF");

    view.setUint32(
        4,
        36 + samples.length * 2,
        true
    );

    writeString(view, 8, "WAVE");

    writeString(view, 12, "fmt ");

    view.setUint32(16, 16, true);

    view.setUint16(20, 1, true);

    view.setUint16(22, 1, true);

    view.setUint32(24, sampleRate, true);

    view.setUint32(
        28,
        sampleRate * 2,
        true
    );

    view.setUint16(32, 2, true);

    view.setUint16(34, 16, true);

    writeString(view, 36, "data");

    view.setUint32(
        40,
        samples.length * 2,
        true
    );

    let index = 44;

    for (let i = 0; i < samples.length; i++) {

        let sample =
            Math.max(-1, Math.min(1, samples[i]));

        sample =
            sample < 0
                ? sample * 0x8000
                : sample * 0x7FFF;

        view.setInt16(
            index,
            sample,
            true
        );

        index += 2;
    }

    return new Blob(
        [buffer],
        { type: "audio/wav" }
    );
}


// Write text into WAV header
function writeString(view, offset, string) {

    for (let i = 0; i < string.length; i++) {

        view.setUint8(
            offset + i,
            string.charCodeAt(i)
        );

    }
}

function speak(text) {

    if (!text) {
        return;
    }

    const speech = new SpeechSynthesisUtterance(text);

    speech.rate = 1;
    speech.pitch = 1;
    speech.volume = 1;

    window.speechSynthesis.cancel();

    window.speechSynthesis.speak(speech);
}

function setStatus(message, state) {

    status.textContent = message;

    statusDot.className = state;
}