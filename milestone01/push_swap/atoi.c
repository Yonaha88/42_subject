/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   atoi.c                                             :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: kyonaha <kyonaha@student.42tokyo.jp>       +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/05/14 10:50:57 by hkanamit          #+#    #+#             */
/*   Updated: 2026/05/18 13:26:19 by kyonaha          ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "push_swap.h"

int	atoi_original(const char *nptr, int *err_flag)
{
	int		i;
	int		minus;
	long	num;

	i = 0;
	minus = 1;
	num = 0;
	if (nptr[i] == '+')
		i++;
	else if (nptr[i] == '-')
	{
		minus = -minus;
		i++;
	}
	while ('0' <= nptr[i] && nptr[i] <= '9')
	{
		num = num * 10 + (nptr[i] - '0');
		i++;
	}
	if (num * minus < -2147483648 || 2147483647 < num * minus)
	{
		*err_flag = -1;
		return (-1);
	}
	return ((int)(num * minus));
}
