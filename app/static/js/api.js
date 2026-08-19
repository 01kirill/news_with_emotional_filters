const API_URL = "/api";

async function fetchNews() {
    const response = await fetch(`${API_URL}/news`);
    if (!response.ok) throw new Error("Ошибка загрузки новостей");
    return await response.json();
}

async function fetchRewrittenNews(newsId, mood, forceUpdate = false) {
    const response = await fetch(`${API_URL}/news/${newsId}/rewrite?mood=${mood}&force_update=${forceUpdate}`, {
        method: "POST"
    });
    if (!response.ok) throw new Error("Ошибка генерации ИИ");
    return await response.json();
}

async function triggerRefreshNews() {
    const response = await fetch(`${API_URL}/news/refresh`, { method: "POST" });
    if (!response.ok) throw new Error("Ошибка обновления ленты");
    return await response.json();
}
