// This file is auto-generated by @hey-api/openapi-ts

export type AccountCreateReadable = {
    email: string;
    disabled?: boolean;
    account_type?: AccountType | null;
    uid?: string | null;
    full_name: string;
};

export type AccountCreateWritable = {
    email: string;
    disabled?: boolean;
    account_type?: AccountType | null;
    uid?: string | null;
    full_name: string;
    password: string;
};

export type AccountProfileMe = {
    email: string;
    disabled?: boolean;
    account_type?: AccountType;
    uid: string;
    full_name: string | null;
    organizations: Array<OrganizationPublic>;
};

export type AccountType = 'user' | 'service-account';

export type BodyConfirmPasswordResetApiV1AccountsConfirmResetPasswordPost = {
    password: string;
};

export type BodyCreatePasswordResetApiV1AccountsResetPasswordPost = {
    email: string;
};

export type BodyLoginApiV1AccountsLoginPost = {
    grant_type?: string | null;
    username: string;
    password: string;
    scope?: string;
    client_id?: string | null;
    client_secret?: string | null;
};

export type HttpValidationError = {
    detail?: Array<ValidationError>;
};

export type OrganizationPublic = {
    public_id: string;
    name: string;
    description: string | null;
    is_default_org?: boolean | null;
    uid: string;
    projects: Array<ProjectPublic>;
    created_at: string;
    updated_at: string;
};

export type ProjectPublic = {
    public_id?: string;
    name: string;
    description: string | null;
    is_default_project?: boolean | null;
    uid: string | null;
};

export type Token = {
    access_token: string;
    refresh_token: string;
    token_type: string;
};

export type TokenRefresh = {
    access_token: string;
    token_type: string;
};

export type ValidationError = {
    loc: Array<string | number>;
    msg: string;
    type: string;
};

export type PostAccountsSignupV1Data = {
    body: AccountCreateWritable;
    path?: never;
    query?: never;
    url: '/api/v1/accounts/signup';
};

export type PostAccountsSignupV1Errors = {
    /**
     * Validation Error
     */
    422: HttpValidationError;
};

export type PostAccountsSignupV1Error = PostAccountsSignupV1Errors[keyof PostAccountsSignupV1Errors];

export type PostAccountsSignupV1Responses = {
    /**
     * Successful Response
     */
    201: Token;
};

export type PostAccountsSignupV1Response = PostAccountsSignupV1Responses[keyof PostAccountsSignupV1Responses];

export type PostAccountsLoginV1Data = {
    body: BodyLoginApiV1AccountsLoginPost;
    path?: never;
    query?: never;
    url: '/api/v1/accounts/login';
};

export type PostAccountsLoginV1Errors = {
    /**
     * Validation Error
     */
    422: HttpValidationError;
};

export type PostAccountsLoginV1Error = PostAccountsLoginV1Errors[keyof PostAccountsLoginV1Errors];

export type PostAccountsLoginV1Responses = {
    /**
     * Successful Response
     */
    200: Token;
};

export type PostAccountsLoginV1Response = PostAccountsLoginV1Responses[keyof PostAccountsLoginV1Responses];

export type GetAccountsProfileMeV1Data = {
    body?: never;
    headers?: {
        'x-api-key'?: string | null;
    };
    path?: never;
    query?: never;
    url: '/api/v1/accounts/profile/me';
};

export type GetAccountsProfileMeV1Errors = {
    /**
     * Validation Error
     */
    422: HttpValidationError;
};

export type GetAccountsProfileMeV1Error = GetAccountsProfileMeV1Errors[keyof GetAccountsProfileMeV1Errors];

export type GetAccountsProfileMeV1Responses = {
    /**
     * Successful Response
     */
    200: AccountProfileMe;
};

export type GetAccountsProfileMeV1Response = GetAccountsProfileMeV1Responses[keyof GetAccountsProfileMeV1Responses];

export type PatchAccountsProfileMeV1Data = {
    body?: never;
    headers?: {
        'x-api-key'?: string | null;
    };
    path?: never;
    query?: never;
    url: '/api/v1/accounts/profile/me';
};

export type PatchAccountsProfileMeV1Errors = {
    /**
     * Validation Error
     */
    422: HttpValidationError;
};

export type PatchAccountsProfileMeV1Error = PatchAccountsProfileMeV1Errors[keyof PatchAccountsProfileMeV1Errors];

export type PatchAccountsProfileMeV1Responses = {
    /**
     * Successful Response
     */
    200: unknown;
};

export type PostAccountsRefreshTokenV1Data = {
    body?: never;
    headers: {
        authorization: string;
    };
    path?: never;
    query?: never;
    url: '/api/v1/accounts/refresh-token';
};

export type PostAccountsRefreshTokenV1Errors = {
    /**
     * Validation Error
     */
    422: HttpValidationError;
};

export type PostAccountsRefreshTokenV1Error = PostAccountsRefreshTokenV1Errors[keyof PostAccountsRefreshTokenV1Errors];

export type PostAccountsRefreshTokenV1Responses = {
    /**
     * Successful Response
     */
    200: TokenRefresh;
};

export type PostAccountsRefreshTokenV1Response = PostAccountsRefreshTokenV1Responses[keyof PostAccountsRefreshTokenV1Responses];

export type PostAccountsResetPasswordV1Data = {
    body: BodyCreatePasswordResetApiV1AccountsResetPasswordPost;
    path?: never;
    query?: never;
    url: '/api/v1/accounts/reset-password';
};

export type PostAccountsResetPasswordV1Errors = {
    /**
     * Validation Error
     */
    422: HttpValidationError;
};

export type PostAccountsResetPasswordV1Error = PostAccountsResetPasswordV1Errors[keyof PostAccountsResetPasswordV1Errors];

export type PostAccountsResetPasswordV1Responses = {
    /**
     * Successful Response
     */
    201: unknown;
};

export type PostAccountsConfirmResetPasswordV1Data = {
    body: BodyConfirmPasswordResetApiV1AccountsConfirmResetPasswordPost;
    headers?: {
        'x-api-key'?: string | null;
    };
    path?: never;
    query?: never;
    url: '/api/v1/accounts/confirm-reset-password';
};

export type PostAccountsConfirmResetPasswordV1Errors = {
    /**
     * Validation Error
     */
    422: HttpValidationError;
};

export type PostAccountsConfirmResetPasswordV1Error = PostAccountsConfirmResetPasswordV1Errors[keyof PostAccountsConfirmResetPasswordV1Errors];

export type PostAccountsConfirmResetPasswordV1Responses = {
    /**
     * Successful Response
     */
    200: unknown;
};

export type HealthCheckHealthGetData = {
    body?: never;
    path?: never;
    query?: never;
    url: '/health';
};

export type HealthCheckHealthGetResponses = {
    /**
     * Successful Response
     */
    200: unknown;
};

export type ClientOptions = {
    baseURL: 'http://localhost:8000' | (string & {});
};