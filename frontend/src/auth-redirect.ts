import { BrowserUtils } from '@azure/msal-browser'

// MSAL v5 popup flow: send auth response to main window via BroadcastChannel
// The main window's loginPopup() waits on BroadcastChannel(libraryState.id) for the payload
try {
  const { payload, libraryState } = BrowserUtils.parseAuthResponseFromUrl()
  const channel = new BroadcastChannel(libraryState.id)
  channel.postMessage({ payload, v: 1 })
  channel.close()
} catch {
  // Not a valid auth response URL (e.g. page loaded directly) — nothing to do
}

window.close()
