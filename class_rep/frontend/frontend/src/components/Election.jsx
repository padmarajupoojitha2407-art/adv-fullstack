import { useState } from "react";

// E1, E2, E6, E10: things every logged-in user can see
export default function Election({ token }) {
    const [candidateId, setCandidateId] = useState("");
    const [message, setMessage] = useState("");

    async function getData(path) {
        const res = await fetch("http://127.0.0.1:8001" + path, {
            method: "GET",
            headers: { "token": token }
        });
        const data = await res.json();
        // the server answer can be a list or an object, so show it as text
        setMessage(JSON.stringify(data, null, 2));
    }
    return (
        <>
            <h2>Election</h2>
            <button onClick={() => getData("/election/phase")}>Show phase</button>
            <button onClick={() => getData("/candidates")}>Show all candidates</button>
            <button onClick={() => getData("/candidates?approved_only=true")}>Show approved candidates</button>
            <input
                placeholder="Candidate id"
                onChange={(e) => setCandidateId(e.target.value)}
            />
            <button onClick={() => getData("/candidates/" + candidateId)}>Show this candidate</button>
            <button onClick={() => getData("/results")}>Show results</button>
            <pre>{message}</pre>
        </>
    );
}
