import { type NextRequest, NextResponse } from "next/server";

export const runtime = "nodejs";

const RAILWAY_URL = "https://assistantmatanne-production.up.railway.app";

type Params = { path: string[] };

async function proxy(
  request: NextRequest,
  context: { params: Promise<Params> }
): Promise<NextResponse> {
  const params = await context.params;
  const targetPath = params.path.join("/");
  const { search } = new URL(request.url);
  const targetUrl = `${RAILWAY_URL}/api/v1/${targetPath}${search}`;

  const reqHeaders = new Headers();
  request.headers.forEach((value: string, key: string) => {
    if (key.toLowerCase() !== "host") {
      reqHeaders.set(key, value);
    }
  });

  const hasBody = request.method !== "GET" && request.method !== "HEAD";
  const body = hasBody ? await request.text() : undefined;

  const response = await fetch(targetUrl, {
    method: request.method,
    headers: reqHeaders,
    body,
  });

  const resText = await response.text();
  const resHeaders = new Headers();
  response.headers.forEach((value: string, key: string) => {
    resHeaders.set(key, value);
  });

  return new NextResponse(resText, {
    status: response.status,
    headers: resHeaders,
  });
}

export const GET = proxy;
export const POST = proxy;
export const PUT = proxy;
export const PATCH = proxy;
export const DELETE = proxy;
export const OPTIONS = proxy;
