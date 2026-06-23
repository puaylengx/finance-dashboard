import type { Configuration } from '@azure/msal-browser'
import { PublicClientApplication } from '@azure/msal-browser'

const clientId = import.meta.env.VITE_AZURE_CLIENT_ID ?? ''
const tenantId = import.meta.env.VITE_AZURE_TENANT_ID ?? ''

export const isMsalConfigured = (): boolean => Boolean(clientId && tenantId)

const msalConfig: Configuration = {
  auth: {
    clientId,
    authority: `https://login.microsoftonline.com/${tenantId}`,
    redirectUri: window.location.origin,
  },
  cache: {
    cacheLocation: 'localStorage',
  },
}

if (clientId && tenantId) {
  try { localStorage.setItem('__msal_cfg', JSON.stringify({ clientId, tenantId })) } catch {}
}

export const msalInstance = new PublicClientApplication(msalConfig)

export const loginScopes = {
  scopes: ['openid', 'profile', `api://${clientId}/access_as_user`],
}
