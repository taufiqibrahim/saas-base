import { AccountProfileMe } from "./client";

export type User = AccountProfileMe & {
    initials: string;
};
