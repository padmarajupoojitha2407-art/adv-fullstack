import { useState } from "react";

// E4 and E7: only the officer can approve and change the phase
export default function Officer({ token }) {
    const [candidateId, setCandidateId] = useState("");
    const [phase, setPhase] = useState("");
    const [message, setMessage] = useState("");

    async function handleApprove() {
        const res = await fetch("http://127.0.0.1:8001/candidates/" + candidateId + "/approve", {
            method: "PATCH",
            headers: { "token": token }
        });
        const data = await res.json();
        setMessage(JSON.stringify(data, null, 2));
    }

    async function handlePhase() {
        const res = await fetch("http://127.0.0.1:8001/election/phase", {
            method: "PATCH",
            headers: { "Content-Type": "application/json", "token": token },
            body: JSON.stringify({
                phase: phase
            })
        });
        const data = await res.json();
        setMessage(JSON.stringify(data, null, 2));
    }
    return (
        <>
            <h2>Approve (officer)</h2>
            <input
                placeholder="Candidate id"
                onChange={(e) => setCandidateId(e.target.value)}
            />
            <button onClick={handleApprove}>Approve</button>

            <h2>Change phase (officer)</h2>
            <input
                placeholder="nominations, voting or closed"
                onChange={(e) => setPhase(e.target.value)}
            />
            <button onClick={handlePhase}>Change phase</button>
            <pre>{message}</pre>
        </>
    );
}
