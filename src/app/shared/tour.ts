export interface Tour {
  id?: string;
  name?: string;
  description?: string;
  activityType?: string;
  source?: string;
  save_path?: string;
  location?: string;
  locations?: string[];
  location_types?: string[];
  countries?: string[];
  region?: string;
  country?: string;
  distance?: number;
  country_short?: string;
  multi_day?: string;
}
