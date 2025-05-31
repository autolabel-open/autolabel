import httpx
from loguru import logger

from config import settings
from utils import JSONType, NotNoneJSONType

client = httpx.AsyncClient(base_url=f"http://{settings.host_port}", timeout=1200.0)
logger.enable("httpx")


class RequestFailedError(Exception):
    pass


async def request_api(
    method: str,
    url: str,
    *,
    content: httpx._types.RequestContent | None = None,
    data: httpx._types.RequestData | None = None,
    files: httpx._types.RequestFiles | None = None,
    json: NotNoneJSONType | None = None,
    params: httpx._types.QueryParamTypes | None = None,
    headers: httpx._types.HeaderTypes | None = None,
    cookies: httpx._types.CookieTypes | None = None,
    auth: (
        httpx._types.AuthTypes | httpx._client.UseClientDefault | None
    ) = httpx._client.USE_CLIENT_DEFAULT,
    follow_redirects: (
        bool | httpx._client.UseClientDefault
    ) = httpx._client.USE_CLIENT_DEFAULT,
    timeout: (
        httpx._types.TimeoutTypes | httpx._client.UseClientDefault
    ) = httpx._client.USE_CLIENT_DEFAULT,
    extensions: httpx._types.RequestExtensions | None = None,
) -> JSONType:
    res = await client.request(
        method,
        url,
        content=content,
        data=data,
        files=files,
        json=json,
        params=params,
        headers=headers,
        cookies=cookies,
        auth=auth,
        follow_redirects=follow_redirects,
        timeout=timeout,
        extensions=extensions,
    )

    res_obj = res.json()
    if res_obj["status"] != "success":
        raise RequestFailedError(res.status_code, res.text)
    return res_obj.get("data")


async def get_api(
    url: str,
    *,
    content: httpx._types.RequestContent | None = None,
    data: httpx._types.RequestData | None = None,
    files: httpx._types.RequestFiles | None = None,
    json: NotNoneJSONType | None = None,
    params: httpx._types.QueryParamTypes | None = None,
    headers: httpx._types.HeaderTypes | None = None,
    cookies: httpx._types.CookieTypes | None = None,
    auth: (
        httpx._types.AuthTypes | httpx._client.UseClientDefault | None
    ) = httpx._client.USE_CLIENT_DEFAULT,
    follow_redirects: (
        bool | httpx._client.UseClientDefault
    ) = httpx._client.USE_CLIENT_DEFAULT,
    timeout: (
        httpx._types.TimeoutTypes | httpx._client.UseClientDefault
    ) = httpx._client.USE_CLIENT_DEFAULT,
    extensions: httpx._types.RequestExtensions | None = None,
) -> JSONType:
    return await request_api(
        "get",
        url,
        content=content,
        data=data,
        files=files,
        json=json,
        params=params,
        headers=headers,
        cookies=cookies,
        auth=auth,
        follow_redirects=follow_redirects,
        timeout=timeout,
        extensions=extensions,
    )


async def post_api(
    url: str,
    *,
    content: httpx._types.RequestContent | None = None,
    data: httpx._types.RequestData | None = None,
    files: httpx._types.RequestFiles | None = None,
    json: NotNoneJSONType | None = None,
    params: httpx._types.QueryParamTypes | None = None,
    headers: httpx._types.HeaderTypes | None = None,
    cookies: httpx._types.CookieTypes | None = None,
    auth: (
        httpx._types.AuthTypes | httpx._client.UseClientDefault | None
    ) = httpx._client.USE_CLIENT_DEFAULT,
    follow_redirects: (
        bool | httpx._client.UseClientDefault
    ) = httpx._client.USE_CLIENT_DEFAULT,
    timeout: (
        httpx._types.TimeoutTypes | httpx._client.UseClientDefault
    ) = httpx._client.USE_CLIENT_DEFAULT,
    extensions: httpx._types.RequestExtensions | None = None,
) -> JSONType:
    return await request_api(
        "post",
        url,
        content=content,
        data=data,
        files=files,
        json=json,
        params=params,
        headers=headers,
        cookies=cookies,
        auth=auth,
        follow_redirects=follow_redirects,
        timeout=timeout,
        extensions=extensions,
    )


async def put_api(
    url: str,
    *,
    content: httpx._types.RequestContent | None = None,
    data: httpx._types.RequestData | None = None,
    files: httpx._types.RequestFiles | None = None,
    json: NotNoneJSONType | None = None,
    params: httpx._types.QueryParamTypes | None = None,
    headers: httpx._types.HeaderTypes | None = None,
    cookies: httpx._types.CookieTypes | None = None,
    auth: (
        httpx._types.AuthTypes | httpx._client.UseClientDefault | None
    ) = httpx._client.USE_CLIENT_DEFAULT,
    follow_redirects: (
        bool | httpx._client.UseClientDefault
    ) = httpx._client.USE_CLIENT_DEFAULT,
    timeout: (
        httpx._types.TimeoutTypes | httpx._client.UseClientDefault
    ) = httpx._client.USE_CLIENT_DEFAULT,
    extensions: httpx._types.RequestExtensions | None = None,
) -> JSONType:
    return await request_api(
        "put",
        url,
        content=content,
        data=data,
        files=files,
        json=json,
        params=params,
        headers=headers,
        cookies=cookies,
        auth=auth,
        follow_redirects=follow_redirects,
        timeout=timeout,
        extensions=extensions,
    )


async def request_rest(
    method: str,
    url: str,
    *,
    content: httpx._types.RequestContent | None = None,
    data: httpx._types.RequestData | None = None,
    files: httpx._types.RequestFiles | None = None,
    json: NotNoneJSONType | None = None,
    params: httpx._types.QueryParamTypes | None = None,
    headers: httpx._types.HeaderTypes | None = None,
    cookies: httpx._types.CookieTypes | None = None,
    auth: (
        httpx._types.AuthTypes | httpx._client.UseClientDefault | None
    ) = httpx._client.USE_CLIENT_DEFAULT,
    follow_redirects: (
        bool | httpx._client.UseClientDefault
    ) = httpx._client.USE_CLIENT_DEFAULT,
    timeout: (
        httpx._types.TimeoutTypes | httpx._client.UseClientDefault
    ) = httpx._client.USE_CLIENT_DEFAULT,
    extensions: httpx._types.RequestExtensions | None = None,
) -> JSONType:
    res = await client.request(
        method,
        url,
        content=content,
        data=data,
        files=files,
        json=json,
        params=params,
        headers=headers,
        cookies=cookies,
        auth=auth,
        follow_redirects=follow_redirects,
        timeout=timeout,
        extensions=extensions,
    )

    if res.status_code >= 400:
        raise RequestFailedError(res.status_code, res.text)
    return res.json()


async def get_rest(
    url: str,
    *,
    content: httpx._types.RequestContent | None = None,
    data: httpx._types.RequestData | None = None,
    files: httpx._types.RequestFiles | None = None,
    json: NotNoneJSONType | None = None,
    params: httpx._types.QueryParamTypes | None = None,
    headers: httpx._types.HeaderTypes | None = None,
    cookies: httpx._types.CookieTypes | None = None,
    auth: (
        httpx._types.AuthTypes | httpx._client.UseClientDefault | None
    ) = httpx._client.USE_CLIENT_DEFAULT,
    follow_redirects: (
        bool | httpx._client.UseClientDefault
    ) = httpx._client.USE_CLIENT_DEFAULT,
    timeout: (
        httpx._types.TimeoutTypes | httpx._client.UseClientDefault
    ) = httpx._client.USE_CLIENT_DEFAULT,
    extensions: httpx._types.RequestExtensions | None = None,
) -> JSONType:
    return await request_rest(
        "get",
        url,
        content=content,
        data=data,
        files=files,
        json=json,
        params=params,
        headers=headers,
        cookies=cookies,
        auth=auth,
        follow_redirects=follow_redirects,
        timeout=timeout,
        extensions=extensions,
    )


async def post_rest(
    url: str,
    *,
    content: httpx._types.RequestContent | None = None,
    data: httpx._types.RequestData | None = None,
    files: httpx._types.RequestFiles | None = None,
    json: NotNoneJSONType | None = None,
    params: httpx._types.QueryParamTypes | None = None,
    headers: httpx._types.HeaderTypes | None = None,
    cookies: httpx._types.CookieTypes | None = None,
    auth: (
        httpx._types.AuthTypes | httpx._client.UseClientDefault | None
    ) = httpx._client.USE_CLIENT_DEFAULT,
    follow_redirects: (
        bool | httpx._client.UseClientDefault
    ) = httpx._client.USE_CLIENT_DEFAULT,
    timeout: (
        httpx._types.TimeoutTypes | httpx._client.UseClientDefault
    ) = httpx._client.USE_CLIENT_DEFAULT,
    extensions: httpx._types.RequestExtensions | None = None,
) -> JSONType:
    return await request_rest(
        "post",
        url,
        content=content,
        data=data,
        files=files,
        json=json,
        params=params,
        headers=headers,
        cookies=cookies,
        auth=auth,
        follow_redirects=follow_redirects,
        timeout=timeout,
        extensions=extensions,
    )
