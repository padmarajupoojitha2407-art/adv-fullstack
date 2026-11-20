import { useState } from "react";

// E3 and E5: only a candidate can nominate or withdraw
export default function Nominate({ token }) {
    const [name, setName] = useState("");
    const [position, setPosition] = useState("");
    const [manifesto, setManifesto] = useState("");
    const [candidateId, setCandidateId] = useState("");
    const [message, setMessage] = useState("");

    async function handleNominate() {
        const res = await fetch("http://127.0.0.1:8001/candidates", {
            method: "POST",
            headers: { "Content-Type": "application/json", "token": token },
            body: JSON.stringify({
                name: name,
                position: position,
                manifesto: manifesto
            })
        });
        const data = await res.json();
        setMessage(JSON.stringify(data, null, 2));
    }

    async function handleWithdraw() {
        const res = await fetch("http://127.0.0.1:8001/candidates/" + candidateId + "/withdraw", {
            method: "PATCH",
            headers: { "token": token }
        });
        const data = await res.json();
        setMessage(JSON.stringify(data, null, 2));
    }
    return (
        <>
            <h2>Nominate (candidate)</h2>
            <input
                placeholder="Name"
                onChange={(e) => setName(e.target.value)}
            />
            <input
                placeholder="class_rep, sports_secretary, cultural_secretary or tech_secretary"
                onChange={(e) => setPosition(e.target.value)}
            />
            <input
                placeholder="Manifesto (at least 30 characters)"
                onChange={(e) => setManifesto(e.target.value)}
            />
            <button onClick={handleNominate}>Nominate</button>

            <h2>Withdraw (candidate)</h2>
            <input
                placeholder="Your candidate id"
                onChange={(e) => setCandidateId(e.target.value)}
            />
            <button onClick={handleWithdraw}>Withdraw</button>
            <pre>{message}</pre>
        </>
    );
}
