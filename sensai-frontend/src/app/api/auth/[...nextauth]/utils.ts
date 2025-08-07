/**
 * Server-side utility functions for authentication
 */

interface UserData {
  email: string;
  given_name?: string;
  family_name?: string;
  name?: string;
  image?: string;
  id?: string;
}

interface AccountData {
  access_token?: string;
  id_token?: string;
  provider?: string;
}

/**
 * Send user authentication data to the backend after successful Google login
 * This is a server-side implementation for NextAuth callbacks
 */
export async function registerUserWithBackend(
  user: UserData,
  account: AccountData
): Promise<any> {
  try {    
    console.log('=== AUTH DEBUG ===');
    console.log('Backend URL:', process.env.BACKEND_URL);
    console.log('User email:', user.email);
    console.log('Account provider:', account.provider);
    console.log('ID token exists:', !!account.id_token);
    console.log('ID token length:', account.id_token?.length || 0);
    console.log('ID token first 20 chars:', account.id_token?.substring(0, 20) || 'NONE');
    
    const response = await fetch(`${process.env.BACKEND_URL}/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        email: user.email,
        given_name: user.given_name || user.name?.split(' ')[0] || '',
        family_name: user.family_name || user.name?.split(' ').slice(1).join(' ') || '',
        id_token: account.id_token
      }),
    });

    console.log('Response status:', response.status);
    
    if (!response.ok) {
      const errorText = await response.text();
      console.log('Error response:', errorText);
      throw new Error(`Backend auth failed: ${response.status} - ${errorText}`);
    }

    // Return the raw response data - assuming it contains an 'id' field directly
    const data = await response.json();
    console.log('Success response:', data);
    
    // Make sure the ID exists and is returned properly
    if (!data.id) {
      console.error("Backend response missing ID field:", data);
    }
    
    return data;
  } catch (error) {
    console.error('Backend authentication error:', error);
    // Don't throw error to prevent blocking the auth flow
    // Just log it and continue
    return { id: null };
  }
} 