import { BrowserUtils } from '@azure/msal-browser'

// MSAL v5 popup flow: send auth response to main window via BroadcastChannel
try {
  const { payload, libraryState } = BrowserUtils.parseAuthResponseFromUrl()
  console.log('[MSAL redirect] parsed, channelId:', libraryState.id)
  const channel = new BroadcastChannel(libraryState.id)
  channel.postMessage({ payload, v: 1 })
  channel.close()
  console.log('[MSAL redirect] broadcast sent')
} catch (e) {
  console.error('[MSAL redirect] failed to parse auth response:', e)
}

window.close()
