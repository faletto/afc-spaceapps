import { httpSource } from './loader';
/** Shared HTTP source for everything under public/data/. */
export const dataSource = httpSource();
export const dataBase = import.meta.env.BASE_URL + 'data/';
