/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   clock.c                                            :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: kyonaha <kyonaha@student.42tokyo.jp>       +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/10/06 12:23:58 by kyonaha           #+#    #+#             */
/*   Updated: 2026/10/29 21:22:29 by kyonaha          ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "codexion.h"

long	now_us(void)
{
	struct timeval	tv;

	gettimeofday(&tv, NULL);
	return (tv.tv_sec * 1000000L + tv.tv_usec);
}

void	sleep_until(t_table *t, long target)
{
	long	left;

	while (!is_stopped(t))
	{
		left = target - now_us();
		if (left <= 0)
			return ;
		if (left > 2 * SLEEP_STEP_US)
			usleep(SLEEP_STEP_US);
		else
			usleep(left / 2 + 1);
	}
}
