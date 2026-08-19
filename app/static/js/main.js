document.addEventListener("DOMContentLoaded", () => {
    let currentNewsId = null;
    let currentMood = null;

    const grid = document.getElementById("news-grid");
    const loadingGrid = document.getElementById("loading-grid");
    const refreshBtn = document.getElementById("refresh-btn");
    const refreshSpinner = document.getElementById("refresh-spinner");

    const newsModal = new bootstrap.Modal(document.getElementById('newsModal'));
    const modalTitle = document.getElementById("modal-title");
    const modalOriginalText = document.getElementById("modal-original-text");
    const modalSourceLink = document.getElementById("modal-source-link");
    const modalRewrittenText = document.getElementById("modal-rewritten-text");
    const aiPlaceholder = document.getElementById("ai-placeholder");
    const aiLoader = document.getElementById("ai-loader");
    const regenerateBtn = document.getElementById("regenerate-btn");
    const moodButtons = document.querySelectorAll(".mood-btn");

    loadNewsGrid();

    async function loadNewsGrid() {
        grid.innerHTML = "";
        grid.appendChild(loadingGrid);
        loadingGrid.classList.remove("d-none");

        try {
            const news = await fetchNews();
            loadingGrid.classList.add("d-none");

            news.forEach(item => {
                const date = new Date(item.published_at).toLocaleString("ru-RU", {
                    day: 'numeric', month: 'short', hour: '2-digit', minute:'2-digit'
                });

                const col = document.createElement("div");
                col.className = "col-12 col-md-6 col-lg-4";
                col.innerHTML = `
                    <div class="card h-100 shadow-sm news-card" data-id="${item.id}">
                        <div class="card-body">
                            <span class="badge bg-secondary mb-2">${item.source_name}</span>
                            <h5 class="card-title fw-bold">${item.title}</h5>
                            <p class="card-text text-muted line-clamp-3">${item.original_text}</p>
                        </div>
                        <div class="card-footer bg-white border-top-0 d-flex justify-content-between align-items-center">
                            <small class="text-muted">${date}</small>
                            <button class="btn btn-sm btn-outline-primary">Читать</button>
                        </div>
                    </div>
                `;

                col.querySelector(".news-card").addEventListener("click", () => openModal(item));
                grid.appendChild(col);
            });
        } catch (error) {
            console.error(error);
            grid.innerHTML = `<div class="alert alert-danger">Не удалось загрузить новости.</div>`;
        }
    }

    function openModal(item) {
        currentNewsId = item.id;
        currentMood = null;

        modalTitle.textContent = item.title;
        modalOriginalText.textContent = item.original_text;
        modalSourceLink.href = item.source_url;

        moodButtons.forEach(btn => btn.checked = false);
        aiPlaceholder.classList.remove("d-none");
        aiLoader.classList.add("d-none");
        modalRewrittenText.classList.add("d-none");
        regenerateBtn.classList.add("d-none");

        newsModal.show();
    }

    moodButtons.forEach(btn => {
        btn.addEventListener("change", (e) => {
            currentMood = e.target.value;
            loadRewrite(currentMood, false);
        });
    });

    regenerateBtn.addEventListener("click", () => {
        if (currentMood) loadRewrite(currentMood, true);
    });

    async function loadRewrite(mood, forceUpdate) {
        aiPlaceholder.classList.add("d-none");
        modalRewrittenText.classList.add("d-none");
        regenerateBtn.classList.add("d-none");
        aiLoader.classList.remove("d-none");

        try {
            const result = await fetchRewrittenNews(currentNewsId, mood, forceUpdate);
            modalRewrittenText.textContent = result.rewritten_text;

            aiLoader.classList.add("d-none");
            modalRewrittenText.classList.remove("d-none");
            regenerateBtn.classList.remove("d-none");
        } catch (error) {
            console.error(error);
            aiLoader.classList.add("d-none");
            modalRewrittenText.textContent = "Произошла ошибка при обращении к ИИ.";
            modalRewrittenText.classList.remove("d-none");
        }
    }

    refreshBtn.addEventListener("click", async () => {
        refreshBtn.disabled = true;
        refreshSpinner.classList.remove("d-none");
        try {
            await triggerRefreshNews();
            await loadNewsGrid();
        } catch (error) {
            alert("Ошибка обновления ленты");
        } finally {
            refreshBtn.disabled = false;
            refreshSpinner.classList.add("d-none");
        }
    });
});
