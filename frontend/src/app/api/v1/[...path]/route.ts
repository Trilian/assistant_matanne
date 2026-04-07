/**
 * Proxy serveur → Railway backend
 * Gère toutes les méthodes HTTP pour /api/v1/*
 */
import { NextRequest, NextResponse } from "next/server";

const RAILWAY_URL = "https://assistantmatanne-production.up.railway.app";

async function proxy(
  request: NextRequest,
  context: { params: Promise<{ path: string[] }> }
) {
  const { path } = await context.params;
  const targetPath = path.join("/");
  const { search } = new URL(request.url);
  const targetUrl = `${RAILWAY_URL}/api/v1/${targetPath}${search}`;

  // Copier les headers (sauf host qui doit pointer vers Railway)
  const reqHeaders = new Headers();
  request.headers.forEach((value, key) => {
    if (key.toLowerCase() !== "host") {
      reqHeaders.set(key, value);
    }
  });

  const body =
    request.method !== "GET" && request.method !== "HEAD"
      ? await request.text()
      : undefined;

  const response = await fetch(targetUrl, {
    method: request.method,
    headers: reqHeaders,
    body,
  });

  const resHeaders = new Headers();
  response.headers.forEach((value, key) => {
    resHeaders.set(key, value);
  });

  return new NextResponse(await response.text(), {
    status: response.status,
    headers: resHeaders,
  });
}

export {
  proxy as GET,
  proxy as POST,
  proxy as PUT,
  proxy as PATCH,
  proxy as DELETE,
  proxy as OPTIONS,
};
