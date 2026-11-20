import { useState } from "react";

// E8 and E9: student and candidate can vote
export default function Vote({ token }) {
    const [candidateId, setCandidateId] = useState("");
    const [rollNo, setRollNo] = useState("");
    const [message, setMessage] = useState("");

    async function handleVote() {
        const res = await fetch("http://127.0.0.1:8001/votes", {
            method: "POST",
            headers: { "Content-Type": "application/json", "token": token },
            body: JSON.stringify({
                candidate_id: candidateId
            })
        });
        const data = await res.json();
        setMessage(JSON.stringify(data, null, 2));
    }

    async function handleVotedPositions() {
        const res = await fetch("http://127.0.0.1:8001/votes/" + rollNo + "/positions", {
            method: "GET",
            headers: { "token": token }
        });
        const data = await res.json();
        setMessage(JSON.stringify(data, null, 2));
    }
    return (
        <>
            <h2>Vote (student, candidate)</h2>
            <input
                placeholder="Candidate id"
                onChange={(e) => setCandidateId(e.target.value)}
            />
            <button onClick={handleVote}>Vote</button>

            <h2>My votes</h2>
            <input
                placeholder="Your roll number"
                onChange={(e) => setRollNo(e.target.value)}
            />
            <button onClick={handleVotedPositions}>Show positions I voted for</button>
            <pre>{message}</pre>
        </>
    );
}
