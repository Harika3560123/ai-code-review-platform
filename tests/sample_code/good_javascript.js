/**
 * Fetch and process user profile data safely.
 * @param {string} userId - Sanitized user identifier.
 * @returns {Promise<object|null>}
 */
async function fetchUserProfile(userId) {
    if (!userId || typeof userId !== "string") {
        throw new Error("Invalid user ID supplied");
    }

    try {
        const response = await fetch(`/api/users/${encodeURIComponent(userId)}`);
        if (!response.ok) {
            throw new Error(`HTTP error: ${response.status}`);
        }
        return await response.json();
    } catch (error) {
        console.error("Failed to fetch user profile:", error);
        return null;
    }
}
