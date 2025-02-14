---
layout: default
title: "Additional Docs"
parent: "AnimeMarketPlace"
nav_order: 5

---
# Additional Documentation
Since we decided to use JS in some places to enhance the WebApp. We will eplain the uses in this section

## General

## Dropdown Menu (Flowbite)

- ## Function: Handles the dropdown menu functionality using Flowbite.
- ## Code:
``` python
<script src="https://cdn.jsdelivr.net/npm/flowbite@3.1.2/dist/flowbite.min.js"></script>
```
## Dropdown Menu

- ## Function: Toggles the visibility of the settings dropdown menu.
- ## Code:
``` python
document.getElementById('dropdownMenuIconButton').addEventListener('click', function() {
  const dropdown = document.getElementById('dropdownGear');
  dropdown.classList.toggle('hidden');
});
```

## Open Chat

- ## Function: Opens the chat for a selected conversation, loads the chat history, and displays product information.
- ## Code:
``` python
function openChat(reqId) {
  // Chatverlauf
  const chatDiv = document.getElementById('chat-' + reqId);
  if (!chatDiv) {
    document.getElementById('chatMessages').innerHTML = '<p class="text-gray-400">No data found.</p>';
    return;
  }
  document.getElementById('chatMessages').innerHTML = chatDiv.innerHTML;

  // Produktinfos
  const listItem = document.querySelector(`li[data-req-id="${reqId}"]`);
  const offerTitle = listItem.getAttribute('data-offer-title') || '';
  const offerPrice = listItem.getAttribute('data-offer-price') || '';
  const offerImage = listItem.getAttribute('data-offer-image') || '';

  document.getElementById('productTitle').textContent = offerTitle;
  document.getElementById('productPrice').textContent = offerPrice ? `€${offerPrice}` : '';

  const imgEl = document.getElementById('productImage');
  if (offerImage && offerImage !== '') {
    imgEl.src = offerImage;
    imgEl.classList.remove('hidden');
  } else {
    imgEl.classList.add('hidden');
  }

  // Formular-Action + Eingabe aktivieren
  document.getElementById('chatForm').action = '/send_response/' + reqId;
  document.getElementById('chatTextarea').disabled = false;
  document.querySelector('#chatForm button[type="submit"]').disabled = false;
}
```

## Auto-Open Chat on Load

- ## Function: Automatically opens the chat for the selected request when the page loads.
- ## Code:
``` python
window.addEventListener('DOMContentLoaded', () => {
  const selReqId = {{ sel_req_id|default(0) }};
  if (selReqId) {
    openChat(selReqId);
  }
});
```
## Marketplace

## Open Modal

- ## Function: Opens a modal to request an offer, sets the form action with the valid offer ID.
- ## Code:
``` python
function openModal(offerId) {
  document.getElementById('offer_id').value = offerId;
  document.getElementById('requestForm').action = `/request_offer/${offerId}`;
  document.getElementById('requestModal').classList.remove('hidden');
}
```
## Close Modal

- ## Function: Closes the request offer modal.
- ## Code:
``` python
function closeModal() {
  document.getElementById('requestModal').classList.add('hidden');
}
```
## My Bookmarks

## Toggle Summary

- ## Function: Toggles the display of the full summary text for an anime.
- ## Code:
``` python
function toggleSummary(id) {
  const summary = document.getElementById(`summary-${id}`);
  const fullText = summary.getAttribute("data-full-text");
  const truncated = fullText.substring(0, 100) + "...";

  if (summary.textContent.endsWith("...")) {
    summary.textContent = fullText;
  } else {
    summary.textContent = truncated;
  }
}
```